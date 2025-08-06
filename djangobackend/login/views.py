
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status,generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegistrationSerializer , LoginSerializer , JobPostingSerializer,ApplicationSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import JobPosting, Application , RegisteredUser
import PyPDF2
from rest_framework.permissions import IsAuthenticated
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
import random
# from .utils import extract_text_from_pdf, calculate_similarity



class RegisterUserView(APIView):

    def get(self , request):
        data = RegisteredUser.objects.all()
        serializer = RegistrationSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User registered successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class LoginSerializerView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)



class jobPostingView(APIView):
    def get(self, request):
        jobs = JobPosting.objects.all()
        serializer = JobPostingSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = JobPostingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class JobApplyView(APIView):
    def get(self, request, id):
        job = get_object_or_404(JobPosting, id=id)
        serializer = JobPostingSerializer(job)
        return Response(serializer.data, status=status.HTTP_200_OK)

class JobUpdate(APIView):
    def put(self , request , id):
        updatedJob = get_object_or_404(JobPosting , id=id)
        updateSerializer = JobPostingSerializer(updatedJob , data = request.data)
        if updateSerializer.is_valid() :
            updateSerializer.save()
            return Response(updateSerializer.data , status=status.HTTP_200_OK)
        return Response(updateSerializer.error , status=status.HTTP_400_BAD_REQUEST)


class CandidateApplicationList(APIView):
    def get(self, request):
        applications = Application.objects.all().order_by('-applied_at')
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



def extract_text_from_pdf(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return ' '.join([page.extract_text() or '' for page in reader.pages])

def calculate_similarity(resume_text, job_text):
    vectorizer = TfidfVectorizer(stop_words='english')
    vectors = vectorizer.fit_transform([resume_text, job_text])
    return cosine_similarity(vectors[0:1], vectors[1:2])[0][0] * 100


class ApplicationCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        serializer = ApplicationSerializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



    def perform_create(self, serializer):
        resume_file = self.request.FILES.get('resume')
        print(resume_file)
        job_id = self.request.data.get('job')  # Make sure 'job' is in form data
        print(job_id)
        job = JobPosting.objects.get(id=job_id)
        
        # Save temporarily without score
        application = serializer.save()

        # Extract text and calculate score
        resume_text = extract_text_from_pdf(application.resume.path)
        print(resume_text)
        similarity_score = calculate_similarity(resume_text, job.requiredSkills)
        
        application.score = similarity_score
        application.save()



#Edit and DELETE functionality in Card.jsx

class JobDelete(APIView):
    def delete(self , request , id):
        try:
            singleData = JobPosting.objects.get(id=id)
            singleData.delete()
            return Response({'message' : "Data deleted successfully"} , status=status.HTTP_204_NO_CONTENT)
        except JobPosting.DoesNotExist:
            return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

# DELETE functionality in Joblist.jsx
class JobApplicant(APIView):
    # permission_classes = [IsAuthenticated]
    def delete(self , request , id):
        try:
            applicantData = Application.objects.get(id=id)
            applicantData.delete()
            return Response({'message' : "Data deleted successfully"} , status=status.HTTP_200_OK)

        except Application.DoesNotExist:
            return Response({'error' : "Applicant not found"} , status=status.HTTP_400_BAD_REQUEST)
        

def generate_otp():
    return str(random.randint(100000, 999999))


class SendOTPEmailView(APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        otp = generate_otp()
        cache.set(f'otp_{email}', otp, timeout=300)  # Store OTP for 5 mins

        try:
            send_mail(
                'Your OTP Code',
                f'Your OTP is: {otp}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return Response({'message': 'OTP sent successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        entered_otp = request.data.get('otp')

        real_otp = cache.get(f'otp_{email}')
        if real_otp is None:
            return Response({'error': 'OTP expired or not sent'}, status=status.HTTP_400_BAD_REQUEST)

        if entered_otp == real_otp:
            return Response({'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid OTP'}, status=status.HTTP_400_BAD_REQUEST)


class SearchPostedJob(APIView):
    def get(self, request):
        search_query = request.GET.get('q', '')

        jobs = JobPosting.objects.all()
        if search_query:
            jobs = jobs.filter(
                title__icontains=search_query
            ) | jobs.filter(
                location__icontains=search_query
            )

        serializer = JobPostingSerializer(jobs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

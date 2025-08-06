
from rest_framework import serializers
from .models import RegisteredUser, JobPosting , Application
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken



class RegistrationSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length = 100)
    email = serializers.EmailField()
    phone = serializers.IntegerField()
    username = serializers.CharField(max_length=10)
    password = serializers.CharField(write_only=True)
    employeeId = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    role = serializers.ChoiceField(choices=RegisteredUser.ROLE_CHOICES, read_only=True)
    # Add any other fields from your RegisteredUser model here manually

    def validate_employeeId(self, value):
        if value == '':
            value = None
        if value and RegisteredUser.objects.filter(employeeId=value).exists():
            raise serializers.ValidationError("This employee ID is already in use.")
        return value

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data['password'])
        return RegisteredUser.objects.create(**validated_data)


#Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = RegisteredUser.objects.filter(email=email).first()

        if user and check_password(password, user.password):
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role,
            }

        raise serializers.ValidationError("Invalid email or password")



class JobPostingSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField()
    jobType = serializers.ChoiceField(choices=JobPosting.JOB_TYPE_CHOICES)
    employmentType = serializers.ChoiceField(choices=JobPosting.EMPLOYMENT_TYPE_CHOICES)
    location = serializers.CharField(max_length=128)
    openings = serializers.IntegerField()
    lastApplyDate = serializers.DateField()
    requiredSkills = serializers.CharField(max_length=255)

    def create(self, validated_data):
        return JobPosting.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.jobType = validated_data.get('jobType', instance.jobType)
        instance.employmentType = validated_data.get('employmentType', instance.employmentType)
        instance.location = validated_data.get('location', instance.location)
        instance.openings = validated_data.get('openings', instance.openings)
        instance.lastApplyDate = validated_data.get('lastApplyDate', instance.lastApplyDate)
        instance.requiredSkills = validated_data.get('requiredSkills', instance.requiredSkills)
        instance.save()
        return instance

#==================================================================================



class ApplicationSerializer(serializers.ModelSerializer):
    jobTitle = serializers.SerializerMethodField()
    class Meta:
        model = Application
        fields = '__all__'
    def get_jobTitle(self, obj):
        return obj.job.title

class CandidateApplication(serializers.ModelSerializer):

    class Meta: 
        model = Application
        fields = '__all__'

from django.db import models
from django.utils import timezone

# Create your models here.
class RegisteredUser(models.Model):
    ROLE_CHOICES = (
        ('User', 'User'),
        ('HR', 'HR'),
    )

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100 , unique=True)
    phone = models.BigIntegerField()  
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=128)
    employeeId = models.CharField(max_length=10, blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='User')

    def save(self, *args, **kwargs):
            # Assign role based on whether employeeId is provided
            self.role = 'HR' if self.employeeId else 'User'
            super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['employeeId'],
                name='unique_employee_id_not_null',
                condition=~models.Q(employeeId__isnull=True) & ~models.Q(employeeId='')
            )
        ]



class JobPosting(models.Model):
    EMPLOYMENT_TYPE_CHOICES = [
    ('Full-time', 'Full-time'),
    ('Part-time', 'Part-time'),
    ('Contract', 'Contract'),
    ('Internship', 'Internship'),
    ('Temporary', 'Temporary'),
    ]
    JOB_TYPE_CHOICES = [
        ('Remote', 'Remote'),
        ('On-site', 'On-site'),
        ('Hybrid', 'Hybrid'),
    ]
    title = models.CharField(max_length=100)
    description = models.TextField()
    jobType = models.CharField(max_length=20 , choices=JOB_TYPE_CHOICES)  
    employmentType = models.CharField(max_length=20, choices=EMPLOYMENT_TYPE_CHOICES)
    location = models.CharField(max_length=128)
    openings = models.IntegerField()
    lastApplyDate = models.DateField()
    requiredSkills = models.CharField(max_length=255)


     
class Application(models.Model):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name='applications')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    skills = models.CharField(max_length=225, null=True, blank=True)
    resume = models.FileField(upload_to='resumes/')
    applied_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} applied for {self.job.title}"
    


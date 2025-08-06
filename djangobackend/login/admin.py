from django.contrib import admin
from .models import RegisteredUser,Application
@admin.register(RegisteredUser)
class RegisteredAdmin(admin.ModelAdmin):
    list_display=['id','name', 'email','phone','username','password','employeeId' , 'role']
# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
        list_display=['id','name', 'email','phone','resume']

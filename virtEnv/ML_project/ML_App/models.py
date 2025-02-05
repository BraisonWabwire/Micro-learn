from django.db import models

# # Create your models here
# class lesson(models.Model):
#     lesson_id = models.AutoField(primary_key=True)
#     course_id = models.IntegerField()  # Assuming this is a foreign key to a Course model
#     title = models.CharField(max_length=255)
#     content = models.TextField()
#     media_type = models.CharField(max_length=50, choices=[('video', 'Video')], default='video')
#     duration = models.DurationField()
#     sequence = models.PositiveIntegerField()
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f" {self.title}-{self.course_id}"


# from django.db import models
# from django.contrib.auth.models import AbstractUser

# class Instructor(models.Model):
#     # Personal Information
#     first_name = models.CharField(max_length=50)
#     last_name = models.CharField(max_length=50)
#     date_of_birth = models.DateField()
#     gender_choices = [
#         ('M', 'Male'),
#         ('F', 'Female'),
#         ('O', 'Other'),
#     ]
#     gender = models.CharField(max_length=1, choices=gender_choices)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15)

#     # Professional Information
#     highest_qualification = models.CharField(max_length=100)
#     area_of_expertise = models.TextField()
#     years_of_experience = models.PositiveIntegerField()
#     resume = models.FileField(upload_to='resumes/')

#     # Account Information
#     username = models.CharField(max_length=50, unique=True)
#     password = models.CharField(max_length=128)

#     # Other Information
#     linkedin_profile = models.URLField(blank=True, null=True)
#     portfolio_website = models.URLField(blank=True, null=True)
#     profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

#     # Agreement Fields
#     terms_agreed = models.BooleanField(default=False)
#     privacy_policy_agreed = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.first_name} {self.last_name} ({self.username})"

    
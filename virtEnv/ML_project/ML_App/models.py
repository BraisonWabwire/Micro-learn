from django.contrib.auth.models import User
from django.db import models

class Instructor(models.Model):
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('ECE', 'Electronics & Communication'),
        ('ME', 'Mechanical Engineering'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor')
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)  # Ensure uniqueness
    instructor_number = models.CharField(max_length=10, unique=True, editable=False)  
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)

    def save(self, *args, **kwargs):
        if not self.instructor_number:
            last_instructor = Instructor.objects.order_by('-id').first()
            if last_instructor and last_instructor.instructor_number.startswith("IN/"):
                num = int(last_instructor.instructor_number.split("/")[-1]) + 1
                self.instructor_number = f"IN/{num:03d}"
            else:
                self.instructor_number = "IN/001"  # Start from IN/001
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

class Course(models.Model):
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to="courses/videos/", blank=True, null=True)
    course_content = models.TextField()  # Can be used with a rich text editor
    course_material = models.FileField(upload_to="courses/materials/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


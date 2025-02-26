from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_instructor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Instructor(models.Model):
    DEPARTMENT_CHOICES = [
        ('CS', 'Computer Science'),
        ('ECE', 'Electronics & Communication'),
        ('ME', 'Mechanical Engineering'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
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
    course_id = models.IntegerField(primary_key=True, unique=True)
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to="videos/", blank=True, null=True)
    course_content = models.TextField()
    course_material = models.FileField(upload_to="materials/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.course_id:
            last_course = Course.objects.order_by('-course_id').first()
            self.course_id = last_course.course_id + 1 if last_course else 1001
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

# Student enrolment model
class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')  # Prevent duplicate enrollments

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"
    


class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_content = models.BooleanField(default=False)  # Track if content is completed
    completed_video = models.BooleanField(default=False)  # Track if video is completed
    completed_material = models.BooleanField(default=False)  # Track if material is completed
    last_accessed = models.DateTimeField(auto_now=True)  # Track last access time

    def __str__(self):
        return f"{self.student.username}'s progress in {self.course.title}"
    def calculate_progress_percentage(self):
        total_items = 3  # Content, Video, Material
        completed_items = 0

        if self.completed_content:
            completed_items += 1
        if self.completed_video:
            completed_items += 1
        if self.completed_material:
            completed_items += 1

        return (completed_items / total_items) * 100
    
# Assignment Model
class Assignment(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)  # Add a title for the assignment
    description = models.TextField(blank=True, null=True)  # Optional description
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()  # The question text

    def __str__(self):
        return self.text

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)  # The choice text
    is_correct = models.BooleanField(default=False)  # Whether this choice is correct

    def __str__(self):
        return self.text

class StudentAssignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_assignments')
    submitted_at = models.DateTimeField(auto_now_add=True)  # Track submission time

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

class StudentAnswer(models.Model):
    student_assignment = models.ForeignKey(StudentAssignment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student_assignment.student.username} - {self.question.text}"
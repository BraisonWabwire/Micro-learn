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
    email = models.EmailField(unique=True)
    instructor_number = models.CharField(max_length=10, unique=True, editable=False)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)

    def save(self, *args, **kwargs):
        if not self.instructor_number:
            last_instructor = Instructor.objects.order_by('-id').first()
            if last_instructor and last_instructor.instructor_number.startswith("IN/"):
                num = int(last_instructor.instructor_number.split("/")[-1]) + 1
                self.instructor_number = f"IN/{num:03d}"
            else:
                self.instructor_number = "IN/001"
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

    def has_all_assignments(self):
        """Check if the course has exactly 3 assignments."""
        return self.assignments.count() == 3

class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

    def can_enroll_next_course(self):
        """Check if student can enroll in the next course."""
        assignments = StudentAssignment.objects.filter(
            student=self.student, 
            assignment__course=self.course
        )
        return (
            assignments.count() == 3 and 
            all(assignment.score >= 7 for assignment in assignments)
        )

class Progress(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progress')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='progress')
    completed_content = models.BooleanField(default=False)
    completed_video = models.BooleanField(default=False)
    completed_material = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.username}'s progress in {self.course.title}"

    def calculate_progress_percentage(self):
        total_items = 3  # Content, Video, Material
        completed_items = sum([
            self.completed_content,
            self.completed_video,
            self.completed_material
        ])
        return (completed_items / total_items) * 100

class Assignment(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    order = models.PositiveIntegerField(default=1, choices=[(1, '1'), (2, '2'), (3, '3')])  # 1, 2, or 3
    max_score = models.PositiveIntegerField(default=10, editable=False)  # Fixed at 10
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('course', 'order')  # Ensure unique order per course
        ordering = ['order']

    def __str__(self):
        return f"{self.title} (Order {self.order})"

class Question(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()

    def __str__(self):
        return self.text

    def calculate_points(self):
        """Calculate points per question based on assignment max_score."""
        total_questions = self.assignment.questions.count()
        return self.assignment.max_score / total_questions if total_questions > 0 else 0

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class StudentAssignment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='student_assignments')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='student_assignments')
    score = models.FloatField(null=True, blank=True)  # Store score out of 10
    completed = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'assignment')

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title}"

    def calculate_score(self):
        """Calculate score based on correct answers."""
        answers = self.answers.all()
        if not answers:
            return 0
        points_per_question = self.assignment.max_score / len(answers)  # Normalize to 10
        correct_answers = sum(1 for answer in answers if answer.selected_choice.is_correct)
        return round(correct_answers * points_per_question, 1)

    def save(self, *args, **kwargs):
        if self.completed and self.score is None:
            self.score = self.calculate_score()
        super().save(*args, **kwargs)

class StudentAnswer(models.Model):
    student_assignment = models.ForeignKey(StudentAssignment, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student_assignment.student.username} - {self.question.text}"
    

from django.utils import timezone

# models.py
class Certificate(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates')
    issued_at = models.DateTimeField(auto_now_add=True)
    certificate_id = models.CharField(max_length=20, unique=True, editable=False)

    def save(self, *args, **kwargs):
        if not self.certificate_id:
            last_cert = Certificate.objects.order_by('-id').first()
            num = int(last_cert.certificate_id.split('-')[-1]) + 1 if last_cert else 1
            self.certificate_id = f"CERT-{timezone.now().strftime('%Y%m%d')}-{num:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate for {self.student.username} - {self.course.title}"
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Instructor, Course, Profile,Enrollment,Progress,Assignment, Question, Choice,StudentAnswer,StudentAssignment
from .forms import InstructorForm, CourseForm, SignupForm, InstructorLoginForm, AssignmentForm, ChoiceForm,QuestionForm
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
from django.contrib.messages import get_messages





# Create your views here.
# Student Handling

def home(request):
    context = {
        'title': 'landing',
    }
    return render(request, 'index.html', context)


def signup(request):
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    form = SignupForm()
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account for {user.username} created successfully")
            return redirect('student_login')
        else:
            # Add specific field errors as messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'email':
                        messages.error(request, f"Email error: {error}")
                    elif field == 'first_name':
                        messages.error(request, f"First name error: {error}")
                    elif field == 'last_name':
                        messages.error(request, f"Last name error: {error}")
                    elif field == 'username':
                        messages.error(request, f"Username error: {error}")
                    elif field == 'password1':
                        messages.error(request, f"Password error: {error}")
                    elif field == 'password2':
                        messages.error(request, f"Password confirmation error: {error}")
                    else:
                        messages.error(request, error)

    context = {
        'title': 'student-signup',
        'form': form
    }
    return render(request, 'student/signup.html', context)

def loginUser(request):

    storage = get_messages(request) 
    context = {
        'title': 'student_login'
        }
    # Check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    if request.method == "POST":
        # Get username and password from the form
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user is an instructor
            profile = Profile.objects.get(user=user)
            if profile.is_instructor:
                # If the user is an instructor, redirect them to the instructor login page
                messages.error(request, 'Instructors must log in using the instructor login form.')
            else:
                # If the user is a student, log them in and redirect to the student dashboard
                login(request, user)
                return redirect('student_dashboard')
        else:
            # If authentication fails, show an error message
            messages.error(request, 'Incorrect username or password.')
        


    return render(request, 'student/login.html', context)



# Student dahsboard i.e also handles assignments

# Existing student_dashboard view (unchanged except context)
@never_cache
@login_required(login_url='student_login')
def student_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.is_instructor:
        return redirect('student_login')

    courses = Course.objects.all()
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    available_courses = courses.exclude(enrollments__student=request.user)

    enrolled_courses_with_progress = []
    completed_courses_with_progress = []

    for course in enrolled_courses:
        progress = Progress.objects.filter(student=request.user, course=course).first()
        if progress:
            progress_percentage = progress.calculate_progress_percentage()
            if progress_percentage == 100:
                completed_courses_with_progress.append({
                    'course': course,
                    'progress_percentage': progress_percentage,
                })
            else:
                enrolled_courses_with_progress.append({
                    'course': course,
                    'progress_percentage': progress_percentage,
                })
        else:
            enrolled_courses_with_progress.append({
                'course': course,
                'progress_percentage': 0,
            })

    student_assignments = StudentAssignment.objects.filter(student=request.user).select_related('assignment__course')
    assignment_results = []
    for student_assignment in student_assignments:
        score, total = calculate_assignment_score(student_assignment)
        percentage = (score / total * 100) if total > 0 else 0
        grade = assign_grade(percentage)
        assignment_results.append({
            'course_title': student_assignment.assignment.course.title,
            'assignment_title': student_assignment.assignment.title,
            'score': score,
            'total': total,
            'percentage': percentage,
            'grade': grade,
        })

    context = {
        'title': 'Student Dashboard',
        'total_courses': courses.count(),
        'available_courses': available_courses,
        'enrolled_courses_with_progress': enrolled_courses_with_progress,
        'completed_courses_with_progress': completed_courses_with_progress,
        'enrolled_courses_count': enrolled_courses.count(),
        'completed_courses_count': len(completed_courses_with_progress),
        'assignment_results': assignment_results,
    }
    return render(request, 'student/dashboard.html', context)

# New AJAX endpoint for chart data
@login_required(login_url='student_login')
def get_chart_data(request):
    profile = get_object_or_404(Profile, user=request.user)
    if profile.is_instructor:
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    # Calculate chart percentages
    courses = Course.objects.all()
    total_courses_count = courses.count()
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    
    completed_count = 0
    in_progress_count = 0
    for course in enrolled_courses:
        progress = Progress.objects.filter(student=request.user, course=course).first()
        if progress and progress.calculate_progress_percentage() == 100:
            completed_count += 1
        else:
            in_progress_count += 1
    
    not_started_count = total_courses_count - (completed_count + in_progress_count)

    if total_courses_count > 0:
        completed_percentage = (completed_count / total_courses_count) * 100
        in_progress_percentage = (in_progress_count / total_courses_count) * 100
        not_started_percentage = (not_started_count / total_courses_count) * 100
    else:
        completed_percentage = 0
        in_progress_percentage = 0
        not_started_percentage = 0

    # Prepare chart data
    chart_data = {
        'labels': ['Completed Courses', 'In Progress Courses', 'Not Started'],
        'datasets': [{
            'data': [completed_percentage, in_progress_percentage, not_started_percentage],
            'backgroundColor': ['#4CAF50', '#FFC107', '#F44336'],
            'borderWidth': 1
        }]
    }

    return JsonResponse(chart_data)

# Culculate assignment score in the student dashboard
def calculate_assignment_score(student_assignment):
    answers = student_assignment.answers.all()
    score = 0
    total = answers.count()
    for answer in answers:
        if answer.selected_choice.is_correct:
            score += 1
    return score, total

# Culculate grade in the students dashboard
def assign_grade(percentage):
    """Assign a letter grade based on percentage."""
    if percentage >= 90:
        return 'A'
    elif percentage >= 80:
        return 'B'
    elif percentage >= 70:
        return 'C'
    elif percentage >= 60:
        return 'D'
    else:
        return 'F'






# Handling user logout
def logoutUser(request):
    logout(request)
    return redirect('student_login')



# Admin views
def admin_login(request):
    if request.method == "POST":
        # Get the submitted username and password
        username = request.POST['username']
        password = request.POST['password']
        
        # Hardcoded admin credentials
        if username == "administrator" and password == "admin01":
            messages.success(request, "Login successful!")
            return redirect('admin_dashboard')  # Redirect to the admin dashboard or another page
        else:
            messages.error(request, "Invalid username or password.")
    context = {
        'title': 'admin-login',
       
    }
    
    return render(request, 'admin/admin_login.html',context)

# Log admin out
def logoutAdmin(request):
    logout(request)
    return redirect('admin_login')

# View for performing CRUD operations on instructor

# Admin dashboard view
def admin_dashboard(request):
    form = InstructorForm()  # Form for adding instructors

    if request.method == "POST":
        form = InstructorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Instructor added successfully.")
            return redirect('admin_dashboard')

    # Fetch all instructors
    instructors = Instructor.objects.all()
    # Fetch all students (users who are not instructors)
    students = User.objects.filter(profile__is_instructor=False)

    # Fetch all users
    all_users = User.objects.all()

    context = {
        'title': 'admin-dashboard',
        'form': form,
        'instructors': instructors,
        'students': students,  # Add students to context
        'users': all_users,  # Add users to context
    }
    return render(request, 'admin/admin_dashboard.html', context)

# New view to delete a student
def delete_student(request, user_id):
    student = get_object_or_404(User, id=user_id)
    # Ensure the user is a student (not an instructor)
    if hasattr(student, 'profile') and not student.profile.is_instructor:
        if request.method == 'POST':
            student.delete()
            messages.success(request, f"Student {student.username} deleted successfully!")
            return redirect('admin_dashboard')
        return render(request, 'admin/confirm_delete_student.html', {'student': student})
    else:
        messages.error(request, "Cannot delete: User is not a student.")
        return redirect('admin_dashboard')
    

#Admin creating instructor
def create_instructor(request):
    if request.method == "POST":
        form = InstructorForm(request.POST)
        if form.is_valid():
            instructor = form.save()  # Save the instructor to the database
            messages.success(request, f"Instructor {instructor.name} added successfully.")
            return redirect('admin_dashboard')  # Redirect to the admin dashboard or another page
        else:
            messages.error(request, "There was an error adding the instructor.")
    else:
        form = InstructorForm()  # Create a blank form if it's a GET request

    # Render the overlay form and pass the form context
    return render(request, 'admin/admin_dashboard.html', {'form': form})

def instructor_update(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    if request.method == "POST":
        form = InstructorForm(request.POST, instance=instructor)
        if form.is_valid():
            form.save()
            messages.success(request, "Instructor updated successfully!")
            return redirect("admin_dashboard")  # Redirect after successful update
        else:
            messages.error(request, "There was an error updating the instructor. Please check the form.")
    else:
        form = InstructorForm(instance=instructor)
    
    return render(request, "admin/update_instructor.html", {"form": form, "instructor": instructor})

def instructor_delete(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    if request.method == 'POST':
        instructor.delete()
        messages.success(request, 'Instructor deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin/confirm_delete.html', {'instructor': instructor})

# Instructor views
def instructor_login(request):
    # Check if user is already authenticated
    # if request.user.is_authenticated:
    #     return redirect('instructor_dashboard')
    
    if request.method == 'POST':
        form = InstructorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                # Check if the user is an instructor
                profile = Profile.objects.get(user=user)
                if profile.is_instructor:
                    # If the user is an instructor, log them in and redirect to the instructor dashboard
                    login(request, user)
                    return redirect('instructor_dashboard')
                else:
                    # If the user is a student, redirect them to the student login page
                    messages.error(request, 'Students must log in using the student login form.')
            else:
                # If authentication fails, show an error message
                messages.error(request, 'Invalid username or password.')
    else:
        form = InstructorLoginForm()
    context={
        'title':'instructor_login',
        'form': form
    }

    return render(request, 'instructor/instructor_login.html', context)


def logoutInstructor(request):
    logout(request)
    return redirect('instructor_login')

@never_cache
@login_required(login_url='instructor_login')
def instructor_dashboard(request):
    # Check if the user is an instructor
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('homepage')  # Redirect to home or another appropriate page
    

    # If the user is not an instructor, redirect them based on their role
    if not profile.is_instructor:
        return redirect('student_dashboard')  # Redirect to student dashboard

    # If the user is an instructor, proceed to the instructor dashboard
    instructor = request.user

    # Get all courses associated with this instructor
    courses = Course.objects.filter(instructor=instructor)

     # Get enrolled students for these courses
    enrollments = Enrollment.objects.filter(course__in=courses).select_related('student', 'course')

     # Fetch progress data for each enrolled student

    #  Assignment form
     # Handle assignment and choices form submission
    if request.method == "POST":
        assignment_form = AssignmentForm(request.POST)
        choice_forms = [ChoiceForm(request.POST, prefix=str(i)) for i in range(4)]  # 4 choices

        if assignment_form.is_valid() and all(cf.is_valid() for cf in choice_forms):
            assignment = assignment_form.save(commit=False)
            assignment.save()  # Save assignment first

            for choice_form in choice_forms:
                choice = choice_form.save(commit=False)
                choice.assignment = assignment  # Assign choices to the assignment
                choice.save()

            return redirect('instructor_dashboard')

    else:
        assignment_form = AssignmentForm()
        choice_forms = [ChoiceForm(prefix=str(i)) for i in range(4)]  # 4 empty choice forms

    assignmentsList= Assignment.objects.all()

    context = {
        'title':'instructor_dashboard',
        'instructor': instructor,
        'username': request.user.username,  # Accessing the username
        'email': request.user.email,        # Accessing the email
        'courses': courses,  # Adding courses to the context
        'enrollments': enrollments, 
        'assignment_form': assignment_form,
        'choice_forms': choice_forms,
        'assignment_list': assignmentsList

    }

    return render(request, 'instructor/instructor_dashboard.html', context)



@login_required(login_url='instructor_login')
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            message=messages.success(request, "Course added successfully!")
            return redirect('add_course')
    else:
        form = CourseForm()

    context={
        'title':'add-course',
        'form':form,
    }
    
    return render(request, 'instructor/add_course.html', context)

@login_required(login_url='instructor_login')
def edit_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id, instructor=request.user)

    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            form.save()
            messages.success(request, "Course updated successfully!")
            return redirect("instructor_dashboard")  # Change this to your actual dashboard route
    else:
        form = CourseForm(instance=course)

    return render(request, "instructor/edit_course.html", {"form": form, "course": course})

@login_required(login_url='instructor_login')
def delete_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id, instructor=request.user)

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect("instructor_dashboard")  # Adjust as needed

    return render(request, "instructor/confirm_delete_course.html", {"course": course})

# Course enrolment handling
@login_required(login_url='student_login')
def enroll_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)

    # Check if the student is already enrolled
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.warning(request, 'You are already enrolled in this course.')
        return redirect('student_dashboard')

    else:
        # Enroll the student in the course
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Successfully enrolled in {course.title}.')

    return redirect('student_dashboard')


# Course content
@login_required(login_url='student_login')
def course_content(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    student = request.user
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_dashboard')

    # Check prior enrolled courses
    enrolled_courses = Enrollment.objects.filter(student=student).order_by('enrolled_at')
    current_course_index = list(enrolled_courses).index(enrollment)
    for prior_enrollment in enrolled_courses[:current_course_index]:
        if not is_course_complete(student, prior_enrollment.course):
            messages.error(request, f'You must complete "{prior_enrollment.course.title}" first.')
            return redirect('student_dashboard')

    assignments = Assignment.objects.filter(course=course)
    progress, created = Progress.objects.get_or_create(student=student, course=course)
    if 'content' in request.GET:
        progress.completed_content = True
    if 'video' in request.GET:
        progress.completed_video = True
    if 'material' in request.GET:
        progress.completed_material = True
    progress.save()

    progress_percentage = progress.calculate_progress_percentage()
    grading_result = None
    if 'score' in request.GET and 'total' in request.GET and 'percentage' in request.GET:
        grading_result = {
            'score': int(request.GET['score']),
            'total': int(request.GET['total']),
            'percentage': float(request.GET['percentage']),
        }

    context = {
        'course': course,
        'progress': progress,
        'progress_percentage': progress_percentage,
        'assignments': assignments,
        'grading_result': grading_result,
    }
    return render(request, 'student/course_content.html', context)

# Displaying the completed courses
@never_cache
@login_required(login_url='student_login')
def completed_courses(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Ensure the user is a student
    if profile.is_instructor:
        return redirect('student_login')

    # Fetch completed courses
    completed_courses_with_progress = []
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)

    for course in enrolled_courses:
        progress = Progress.objects.filter(student=request.user, course=course).first()
        if progress and progress.calculate_progress_percentage() == 100:
            completed_courses_with_progress.append({
                'course': course,
                'progress_percentage': 100,
            })

    context = {
        'title': 'Completed Courses',
        'completed_courses_with_progress': completed_courses_with_progress,
    }

    return render(request, 'student/completed_courses.html', context)

# views.py (at the top)
def is_course_complete(student, course):
    # Check progress (100%)
    progress = Progress.objects.filter(student=student, course=course).first()
    if not progress or progress.calculate_progress_percentage() != 100:
        return False
    
    # Check all assignments passed (≥ 7/10)
    assignments = Assignment.objects.filter(course=course)
    student_assignments = StudentAssignment.objects.filter(student=student, assignment__course=course)
    if assignments.count() != student_assignments.count():  # All must be attempted
        return False
    return all(sa.completed and sa.score >= 7 for sa in student_assignments)


@login_required(login_url='instructor_login')
def create_assignment(request, course_id):
    # Ensure the course exists and belongs to the requesting instructor
    course = get_object_or_404(Course, course_id=course_id, instructor=request.user)
    assignment = None
    question = None
    error_message = None

    # Check current number of assignments
    assignments = Assignment.objects.filter(course=course)
    current_assignment_count = assignments.count()
    if current_assignment_count >= 3:
        error_message = "This course already has the maximum of 3 assignments."
    elif request.user != course.instructor:
        error_message = "You can only add assignments to your own courses."

    # Handle Assignment Form Submission
    if 'assignment_form' in request.POST and not error_message:
        assignment_form = AssignmentForm(request.POST)
        if assignment_form.is_valid():
            assignment = assignment_form.save(commit=False)
            assignment.course = course
            assignment.order = current_assignment_count + 1  # Set order (1, 2, or 3)
            assignment.max_score = 10  # Fixed as per model, but explicitly set here
            assignment.save()
            print(f"Assignment created: {assignment.title} (Order {assignment.order}) for course: {course.title}")
            return redirect('create_assignment', course_id=course.course_id)
        else:
            print("Form errors:", assignment_form.errors)
    else:
        assignment_form = AssignmentForm()

    # Get the latest assignment for display (if any)
    if assignments.exists():
        assignment = assignments.latest('created_at')

    # Handle Question Form Submission
    if 'question_form' in request.POST:
        assignment_id = request.POST.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id, course=course)
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.assignment = assignment
            question.save()
            print(f"Question added to Assignment {assignment.order}: {question.text}")
            return redirect('create_assignment', course_id=course.course_id)
    else:
        question_form = QuestionForm()

    # Get the latest question for display (if any)
    if assignment:
        questions = Question.objects.filter(assignment=assignment)
        if questions.exists():
            question = questions.latest('id')

    # Handle Choice Form Submission
    if 'choice_form' in request.POST:
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, id=question_id, assignment__course=course)
        choice_form = ChoiceForm(request.POST)
        if choice_form.is_valid():
            choice = choice_form.save(commit=False)
            choice.question = question
            choice.save()
            print(f"Choice added to Question: {choice.text} (Correct: {choice.is_correct})")
            return redirect('create_assignment', course_id=course.course_id)
    else:
        choice_form = ChoiceForm()

    # Fetch all related data for display
    questions = Question.objects.filter(assignment__course=course)
    choices = Choice.objects.filter(question__assignment__course=course)

    context = {
        'course': course,
        'assignment_form': assignment_form,
        'question_form': question_form,
        'choice_form': choice_form,
        'assignments': assignments,
        'questions': questions,
        'choices': choices,
        'assignment': assignment,
        'question': question,
        'error_message': error_message,
    }
    return render(request, 'instructor/create_assignment.html', context)

def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    return redirect('instructor_dashboard') 

@login_required(login_url='student_login')
def take_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    student = request.user
    course = assignment.course

    # Check enrollment
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        return render(request, 'student/take_assignment.html', {
            'assignment': assignment,
            'error': 'You are not enrolled in this course.',
        })

    # Check prior enrolled courses
    enrolled_courses = Enrollment.objects.filter(student=student).order_by('enrolled_at')
    current_course_index = list(enrolled_courses).index(enrollment)
    for prior_enrollment in enrolled_courses[:current_course_index]:
        if not is_course_complete(student, prior_enrollment.course):
            return render(request, 'student/take_assignment.html', {
                'assignment': assignment,
                'error': f'You must complete "{prior_enrollment.course.title}" first.',
            })

    # Existing prerequisite check for assignments within the course
    if assignment.order > 1:
        prev_assignment = Assignment.objects.filter(course=course, order=assignment.order - 1).first()
        if prev_assignment:
            prev_submission = StudentAssignment.objects.filter(student=student, assignment=prev_assignment).first()
            if not prev_submission or prev_submission.score < 7:
                return render(request, 'student/take_assignment.html', {
                    'assignment': assignment,
                    'error': f'You must score at least 7/10 on Assignment {prev_assignment.order} first.',
                })

    # Check if already completed
    existing_submission = StudentAssignment.objects.filter(student=student, assignment=assignment).first()
    if existing_submission and existing_submission.completed:
        return redirect(reverse('course_content', kwargs={'course_id': course.course_id}))

    questions = assignment.questions.all()
    if not questions.exists():
        return render(request, 'student/take_assignment.html', {
            'assignment': assignment,
            'error': 'This assignment has no questions yet.',
        })

    if request.method == "POST":
        student_assignment = StudentAssignment.objects.create(student=student, assignment=assignment)
        for question in questions:
            selected_choice_id = request.POST.get(f"question_{question.id}")
            if selected_choice_id:
                selected_choice = get_object_or_404(Choice, id=selected_choice_id, question=question)
                StudentAnswer.objects.create(
                    student_assignment=student_assignment,
                    question=question,
                    selected_choice=selected_choice
                )
        student_assignment.completed = True
        student_assignment.save()
        return redirect(reverse('course_content', kwargs={'course_id': course.course_id}))

    context = {
        'assignment': assignment,
        'questions': questions,
    }
    return render(request, 'student/take_assignment.html', context)


def calculate_assignment_score(student_assignment):
    """
    Calculate the score for a student assignment, normalized to 10.
    This is now primarily handled in the StudentAssignment model's save method,
    but kept here for reference or external use.
    """
    answers = student_assignment.answers.all()
    if not answers.exists():
        return 0, 10
    points_per_question = student_assignment.assignment.max_score / answers.count()  # 10 / number of questions
    correct_answers = sum(1 for answer in answers if answer.selected_choice.is_correct)
    score = round(correct_answers * points_per_question, 1)
    return score, student_assignment.assignment.max_score  # Always returns total as 10




# Other pages
def privacy_policy(request):
    return render(request, 'privacy_policy.html')
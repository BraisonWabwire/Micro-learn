from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Instructor, Course, Profile,Enrollment,Progress,Assignment, Question, Choice,StudentAnswer,StudentAssignment
from .forms import InstructorForm, CourseForm, SignupForm, InstructorLoginForm, AssignmentForm, ChoiceForm,QuestionForm
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt





# Create your views here.
# Student Handling

def home(request):
    context = {
        'title': 'homepage',
    }
    return render(request, 'index.html', context)

def signup(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    else:
        # Perform the signup
        form = SignupForm()
        if request.method == "POST":
            form = SignupForm(request.POST)
            if form.is_valid():
                user = form.save()
                messages.success(request, f"Account for {user.username} created successfully")
                return redirect('student_login')
            else:    
                messages.error(request, f"Please check your credentials")

        context = {
            'title': 'student-signup',
            'form': form
        }
    return render(request, 'student/signup.html', context)

def loginUser(request):
    # Check if user is already authenticated
    if request.user.is_authenticated:
        return redirect('student_dashboard')
    
    context = {
        'title': 'student_login'
    }

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

# Student dahsboard
@never_cache
@login_required(login_url='student_login')
def student_dashboard(request):
    profile = get_object_or_404(Profile, user=request.user)

    # Ensure the user is a student
    if profile.is_instructor:
        return redirect('student_login')

    # Fetching courses
    courses = Course.objects.all()
    enrolled_courses = Course.objects.filter(enrollments__student=request.user)
    available_courses = courses.exclude(enrollments__student=request.user)

    # Fetch progress for each enrolled course and separate completed courses
    enrolled_courses_with_progress = []
    completed_courses_with_progress = []  # List for completed courses

    for course in enrolled_courses:
        progress = Progress.objects.filter(student=request.user, course=course).first()
        if progress:
            progress_percentage = progress.calculate_progress_percentage()
            # Check if the course is completed (100% progress)
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
            # If no progress exists, assume the course is not started
            enrolled_courses_with_progress.append({
                'course': course,
                'progress_percentage': 0,
            })

    
    context = {
        'title': 'Student Dashboard',
        'total_courses': courses.count(),
        'available_courses': available_courses,
        'enrolled_courses_with_progress': enrolled_courses_with_progress,  # Pass enrolled courses (not completed)
        'completed_courses_with_progress': completed_courses_with_progress,  # Pass completed courses
        'enrolled_courses_count': enrolled_courses.count(),
        'completed_courses_count': len(completed_courses_with_progress),  # Count of completed courses
    }

    return render(request, 'student/dashboard.html', context)



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
def admin_dashboard(request):
    form = InstructorForm()  # Ensure form is always passed

    if request.method == "POST":
        form = InstructorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Instructor added successfully.")
            return redirect('admin_dashboard')

    instructors = Instructor.objects.all()  # Fetch existing instructors
    context = {
        'title': 'admin-dashboard',
        'form': form,
        'instructors': instructors,
       
    }
    return render(request, 'admin/admin_dashboard.html', context)

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

    # Check if the student is enrolled in the course
    enrollment = Enrollment.objects.filter(student=student, course=course).first()
    if not enrollment:
        messages.error(request, 'You are not enrolled in this course.')
        return redirect('student_dashboard')

    # Get or create progress for the student in this course
    progress, created = Progress.objects.get_or_create(student=student, course=course)

    # Update progress based on what the student accesses
    if 'content' in request.GET:
        progress.completed_content = True
    if 'video' in request.GET:
        progress.completed_video = True
    if 'material' in request.GET:
        progress.completed_material = True
    progress.save()

    # Calculate progress percentage
    progress_percentage = progress.calculate_progress_percentage()
    assignments = Assignment.objects.filter(course=course)

    context = {
        'course': course,
        'progress': progress,
        'progress_percentage': progress_percentage,
        'assignments':assignments 
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

# Create assignment
@login_required(login_url='instructor_login')
def create_assignment(request, course_id):
    course = get_object_or_404(Course, course_id=course_id)
    assignment = None
    question = None

    # Handle Assignment Form Submission
    if 'assignment_form' in request.POST:
        assignment_form = AssignmentForm(request.POST)
        if assignment_form.is_valid():
            assignment = assignment_form.save(commit=False)
            assignment.course = course
            assignment.save()
            return redirect('create_assignment', course_id=course.course_id)
    else:
        assignment_form = AssignmentForm()

    # Get the latest assignment for this course (if available)
    assignments = Assignment.objects.filter(course=course)
    if assignments.exists():
        assignment = assignments.latest('created_at')

    # Handle Question Form Submission
    if 'question_form' in request.POST:
        assignment_id = request.POST.get('assignment_id')
        assignment = get_object_or_404(Assignment, id=assignment_id)
        question_form = QuestionForm(request.POST)
        if question_form.is_valid():
            question = question_form.save(commit=False)
            question.assignment = assignment
            question.save()
            return redirect('create_assignment', course_id=course.course_id)
    else:
        question_form = QuestionForm()

    # Get the latest question for this assignment (if available)
    if assignment:
        questions = Question.objects.filter(assignment=assignment)
        if questions.exists():
            question = questions.latest('id')

    # Handle Choice Form Submission
    if 'choice_form' in request.POST:
        question_id = request.POST.get('question_id')
        question = get_object_or_404(Question, id=question_id)
        choice_form = ChoiceForm(request.POST)
        if choice_form.is_valid():
            choice = choice_form.save(commit=False)
            choice.question = question
            choice.save()
            return redirect('create_assignment', course_id=course.course_id)
    else:
        choice_form = ChoiceForm()

    # Fetch all related data
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
    }
    return render(request, 'instructor/create_assignment.html', context)



def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    assignment.delete()
    return redirect('instructor_dashboard') 




@login_required
def take_assignment(request, assignment_id):
    # Get the assignment
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)

    # Check if the student has already submitted the assignment
    existing_submission = StudentAssignment.objects.filter(student=request.user, assignment=assignment).first()
    if existing_submission:
        return redirect('assignment_result', existing_submission.id)  # ✅ Fix: Correct redirect

    questions = assignment.questions.all()  # Get questions related to the assignment

    if request.method == "POST":
        # Create a new StudentAssignment record
        student_assignment = StudentAssignment.objects.create(student=request.user, assignment=assignment)

        # Store student answers
        for question in questions:
            selected_choice_id = request.POST.get(f"question_{question.id}")
            if selected_choice_id:
                selected_choice = get_object_or_404(Choice, id=selected_choice_id)  # Fix: Use `get_object_or_404`
                StudentAnswer.objects.create(
                    student_assignment=student_assignment,
                    question=question,
                    selected_choice=selected_choice
                )

        return redirect('assignment_result', student_assignment.id)  # Fix: Correct redirect

    context = {
        'assignment': assignment,
        'questions': questions,
    }

    return render(request, 'take_assignment.html', context)

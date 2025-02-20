from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Instructor, Course, Profile
from .forms import InstructorForm, CourseForm, SignupForm, InstructorLoginForm

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
                return redirect('login')
            else:
                print(form.errors)

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
        'title': 'login'
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


@login_required(login_url='login')
def student_dashboard(request):
    courses = Course.objects.all() 
    total_courses = courses.count()

    context = {
        'title': 'Student Dashboard',
        'total_courses': total_courses,
        # 'courses': courses,
    }
    return render(request, 'student/dashboard.html', context)

# Handling user logout
def logoutUser(request):
    logout(request)
    return redirect('login')





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
        'title': 'admin-login',
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
    if request.user.is_authenticated:
        return redirect('instructor_dashboard')
    
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
                    messages.success(request, 'Login successful!')
                    return redirect('instructor_dashboard')
                else:
                    # If the user is a student, redirect them to the student login page
                    messages.error(request, 'Students must log in using the student login form.')
            else:
                # If authentication fails, show an error message
                messages.error(request, 'Invalid username or password.')
    else:
        form = InstructorLoginForm()

    return render(request, 'instructor/instructor_login.html', {'form': form})




def logoutInstructor(request):
    logout(request)
    return redirect('instructor_login')

@login_required
def instructor_dashboard(request):
    # Access the instructor associated with the logged-in user
    instructor = request.user  # Assuming instructors use the Django User model

    # Get all courses associated with this instructor
    courses = Course.objects.filter(instructor=instructor)

    context = {
        'instructor': instructor,
        'username': request.user.username,  # Accessing the username
        'email': request.user.email,        # Accessing the email
        'courses': courses,  # Adding courses to the context
    }
    return render(request, 'instructor/instructor_dashboard.html', context)

@login_required
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, "Course added successfully!")
            return redirect('instructor_dashboard')
    else:
        form = CourseForm()
    
    return render(request, 'instructor/add_course.html', {'form': form})

@login_required
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

@login_required
def delete_course(request, course_id):
    course = get_object_or_404(Course, course_id=course_id, instructor=request.user)

    if request.method == "POST":
        course.delete()
        messages.success(request, "Course deleted successfully!")
        return redirect("instructor_dashboard")  # Adjust as needed

    return render(request, "instructor/confirm_delete_course.html", {"course": course})
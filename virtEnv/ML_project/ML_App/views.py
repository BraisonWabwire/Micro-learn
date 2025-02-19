from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .models import Instructor
from .forms import InstructorForm
from django.http import JsonResponse
from .models import Course
from .forms import CourseForm


# Create your views here.
# Student Handling
from .forms import SignupForm

def home(request):
    context={
        'title':'homepage',
    }
    return render(request,'index.html',context)

def signup(request):
    #Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        # Perform the signup
        form=SignupForm()
        if request.method=="POST":
            form=SignupForm(request.POST)
            if form.is_valid:
                form.save()
                user=form.cleaned_data.get('username')
                messages.success(request, user + "account created successfully")
                return redirect('login')
            
            else:
                print(form.errors)

        context={
            'title': 'student-signup',
            'form': form
        }
    return render(request,'student/signup.html', context)

def loginUser(request):
    # Check if user is authenticated
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        context={
            'title':'login'
        }
        if request.method=="POST":
            # Getting username and password from the form
            username=request.POST.get('username')
            password=request.POST.get('password')

            # Checking if user is authenticated
            user=authenticate(request, username=username, password=password)

            # Check if user is in the available
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request,'incorrect username or password ')


            context={
                'title':'login'
            }
    return render(request,'student/login.html', context)

@login_required(login_url='login')
def dashbord(request):
    context={
        'title':'student-dashboard',
    }
    return render(request, 'student/dashboard.html', context)

# Handling user logout
def logoutUser(request):
    logout(request)
    return redirect('login')





# Admin handling
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
    
    return render(request, 'admin/admin_login.html')

# Log admin out
def logoutAdmin(request):
    logout(request)
    return redirect('admin_login')


# View for performing CRUD operations on instructor
# @login_required(login_url='admin_login')
def admin_dashboard(request):
    form = InstructorForm()  # Ensure form is always passed

    if request.method == "POST":
        form = InstructorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Instructor added successfully.")
            return redirect('admin_dashboard')

    instructors = Instructor.objects.all()  # Fetch existing instructors
    return render(request, 'admin/admin_dashboard.html', {'form': form, 'instructors': instructors})

# @login_required(login_url='admin_login')
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

# @login_required(login_url='admin_login')
from .models import Instructor
from .forms import InstructorForm

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


# @login_required(login_url='admin_login')
def instructor_delete(request, id):
    instructor = get_object_or_404(Instructor, id=id)
    if request.method == 'POST':
        instructor.delete()
        messages.success(request, 'Instructor deleted successfully!')
        return redirect('admin_dashboard')
    return render(request, 'admin/confirm_delete.html', {'instructor': instructor})




# Instructor views

from .forms import InstructorLoginForm
def instructor_login(request):
    if request.method == 'POST':
        form = InstructorLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, 'Login successful!')
                return redirect('instructor_dashboard')  # Replace 'dashboard' with your desired redirect view
            else:
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

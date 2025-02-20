from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='homepage'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.loginUser, name='login'),
    path('student/dashboard/',views.student_dashboard,name='student_dashboard'),
    path('logout/',views.logoutUser,name='logout'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('logoutAdmin/',views.logoutAdmin,name='logoutAdmin'),
    path('create_instructor/',views.create_instructor, name='create_instructor'),
    path('instructors/update/<int:id>/', views.instructor_update, name='instructor_update'),
    path('instructors/delete/<int:id>/', views.instructor_delete, name='instructor_delete'),
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/instructor_logout/', views.logoutInstructor, name='instructor_logout'),
    path('instructor_dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('add_course/', views.add_course, name='add_course'),
    path("edit-course/<int:course_id>/", views.edit_course, name="edit_course"),
    path("delete-course/<int:course_id>/", views.delete_course, name="delete_course"),

]
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.home, name='homepage'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.loginUser, name='student_login'),
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
    path('course/<int:course_id>/create_assignment/', views.create_assignment, name='create_assignment'),
    path('assignments/delete/<int:assignment_id>/', views.delete_assignment, name='delete_assignment'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/', views.course_content, name='course_content'),
    path('completed-courses/', views.completed_courses, name='completed_courses'),
    path('take_assignment/<int:assignment_id>/', views.take_assignment, name='take_assignment'),
    # Get chart data
    path('get_chart_data/', views.get_chart_data, name='get_chart_data'),
    path('admin/student/delete/<int:user_id>/', views.delete_student, name='delete_student'),

    # Other urls
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('report/', views.generate_student_report, name='student_report'),
    path('student/certificate/<int:course_id>/', views.generate_certificate, name='generate_certificate'),

]   

# For handling video display
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
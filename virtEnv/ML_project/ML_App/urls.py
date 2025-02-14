from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='homepage'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.loginUser, name='login'),
    path('dashbord/',views.dashbord,name='dashbord'),
    path('logout/',views.logoutUser,name='logout'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('logoutAdmin/',views.logoutAdmin,name='logoutAdmin'),
    path('instructor_dash/',views.instructor_dash, name='instructor_dash'),
    
    
]
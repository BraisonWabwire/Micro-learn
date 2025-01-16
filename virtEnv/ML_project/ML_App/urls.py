from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='homepage'),
    path('signup/',views.signup,name='signup'),
    path('login/',views.loginUser, name='login'),
    path('dashbord/',views.dashbord,name='dashbord'),
    path('logout/',views.logoutUser,name='logout'),
    
]
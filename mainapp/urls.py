from django.urls import path 
from . import views

urlpatterns = [
    path('',views.index,name = 'index'),
    path('dashboard/',views.dashboard,name='dashboard'),
    path('initiate_payment/',views.initiate_payment,name = 'initiate_payment'),
    path('send_pocket_money',views.send_pocket_money,name= 'send_pocket_money'),
    path('student_login/', views.student_login, name = 'student_login'),
    path('school_search/',views.school_search,name= 'school_search'),
    path('add_student/', views.add_student, name='add_student'),
    path('add_school/', views.add_school, name='add_school'),
    
]

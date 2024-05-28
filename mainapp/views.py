import requests
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import JsonResponse,HttpResponse
from .models import School, Student, Pocket_money
from django.db import models
from django.db.models import Sum,F
from .paym import initiate_ecitizen_payment, initiate_pocket_money_payment
from .models import Student, School



def index(request):
    schools = School.objects.all()
    return render(request, 'index.html',{'schools': schools})


def school_search(request):
    query = request.GET.get('search_query', '')
    if query:
        schools = School.objects.filter(name__icontains=query)
    else:
        schools = School.objects.all()
    return render(request, 'school_page.html', {'schools': schools})



def initiate_payment(request):
    if request.method == 'POST':
        # Retrieve form data
        amount = request.POST['amount']
        phone_number = request.POST['phone_number']
        admission = request.POST['admission_number']
        response = initiate_ecitizen_payment(amount, phone_number,admission)
        if response.get('success', False):
            # Payment initiated successfully
            return JsonResponse({'success': True, 'message': 'Payment initiated successfully'})
        else:
            # Payment initiation failed
            error_message = response.get('message', 'Payment initiation failed')
            return JsonResponse({'success': False, 'message': error_message})
    return render(request,'paymentform.html')




def send_pocket_money(request):
    if request.method == 'POST':
        guardian_first_name = request.POST['first_name']
        guardian_last_name = request.POST['last_name']
        student_first_name = request.POST['student_first_name']
        student_last_name = request.POST['student_last_name']
        admission_number = request.POST['admission_number']
        amount = request.POST['amount']
        phone_number = request.POST['phone_number']

        response = initiate_pocket_money_payment(student_first_name,amount, phone_number,admission_number)
        if response.get('success', False):
            # Payment initiated successfully
            pocket_money = Pocket_money(guardian_first_name=guardian_first_name,
                                        guardian_last_name=guardian_last_name,
                                        student_first_name=student_first_name,
                                        student_last_name=student_last_name,
                                        admission_number=admission_number,
                                        pocket_amount=amount)
            pocket_money.save()
            return JsonResponse({'success': True, 'message': 'Payment initiated successfully'})
        else:
            # Payment initiation failed
            error_message = response.get('message', 'Payment initiation failed')
            return JsonResponse({'success': False, 'message': error_message})
    return render(request, 'pocket_money.html')

    


def student_login(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST('last_name')
        reg_no = request.POST.get('reg_no',False)
        try:
            student = Student.objects.get(student_first_name=first_name, student_last_name=last_name, admission_number=reg_no)
            return render(request, 'student_details.html', {'student': student})
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'})
    return render(request, 'student_login.html')



def dashboard(request):
        # Compute total fee paid and total fee due
    total_fee_paid = Student.objects.aggregate(models.Sum('total_fee_paid'))['total_fee_paid__sum'] or 0
    total_fee_due = Student.objects.aggregate(models.Sum('fee_balance'))['fee_balance__sum'] or 0
    students = Student.objects.all()
    

    context = {
              'total_fee_paid': total_fee_paid,
              'total_fee_due': total_fee_due,
              'students': students,
             }
    return render(request, 'dashboard.html', context)




def fetch_student_data(request):
    # Fetch all students
    students = Student.objects.all()

    # Serialize student data
    student_data = [{'student_first_name': student.student_first_name,
                     'student_last_name': student.student_last_name,
                     'parent_phone': student.parent_phone,
                     'admission_number': student.admission_number,
                     'total_fee_paid': student.total_fee_paid,
                     'fee_balance': student.fee_balance} for student in students]

    # Return serialized data as JSON response
    return JsonResponse({'students': student_data})




def add_school(request):
    if request.method == 'POST':
        school_name = request.POST.get('school_name')
        registration_number = request.POST.get('registration_number')
        email = request.POST.get('email')

        # Create and save a new School instance
        School.objects.create(school_name=school_name, registration_number=registration_number, email=email)
        
        return redirect('dashboard')  # Redirect to the same page after adding a school

    return render(request, 'add_school.html')



def add_student(request):
    if request.method == 'POST':
        student_first_name = request.POST.get('student_first_name')
        student_last_name = request.POST.get('student_last_name')
        admission_number = request.POST.get('admission_number')
        total_fee_paid = request.POST.get('total_fee_paid')
        fee_balance = request.POST.get('fee_balance')

        # Create and save a new Student instance
        Student.objects.create(
            student_first_name=student_first_name,
            student_last_name=student_last_name,
            admission_number=admission_number,
            total_fee_paid=total_fee_paid,
            fee_balance=fee_balance
        )

        return redirect('add_student')  # Redirect to the same page after adding a student

    schools = School.objects.all()
    return render(request, 'add_student_and_school.html', {'schools': schools})








from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

class School(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length =  100 ,null = False)

    def __str__(self):
        return self.name

class Pocket_money(models.Model):
    gudian_first_name = models.CharField(max_length = 100)
    gudian_last_name = models.CharField(max_length = 100)
    student_first_name = models.CharField(max_length = 100)
    student_last_name = models.CharField(max_length = 100)
    admission_number = models.CharField(max_length = 100)
    pocket_amount = models.DecimalField(max_digits = 10,decimal_places = 2)

    def __str__(self):
        return str(self.pocket_amount)

 


class Student(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    student_first_name = models.CharField(max_length = 100,null=False,blank=False)
    student_last_name = models.CharField(max_length = 100,null = False,blank=False)
    parent_phone = models.CharField(max_length=20)
    admission_number = models.CharField(max_length = 100)
    pocket_money = models.OneToOneField(Pocket_money, on_delete=models.CASCADE)
    total_fee_paid = models.DecimalField(max_digits=10, decimal_places=2,null = False)
    fee_balance = models.DecimalField(max_digits=10, decimal_places=2)


    def __str__(self):
        return f'NAME: {self.student_first_name} {self.student_last_name}, FEE PAID: {str(self.total_fee_paid)},FEE BALANCE: {str(self.fee_balance)},POCKET MONEY BALANCE: {str(self.pocket_money.pocket_amount)}'


class Payment(models.Model):
    transaction_id = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=13)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    checkout_request_id = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    transaction_date = models.DateTimeField()
    user_email = models.EmailField()

    def __str__(self):
        return self.transaction_id




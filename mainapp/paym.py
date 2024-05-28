import datetime 
import requests
import json
from django.http import JsonResponse
from requests.auth import HTTPBasicAuth
import base64
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment
import json

def get_access_token():
    consumer_key = 'consumer key'
    consumer_secret = 'consumer secret'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.get(api_URL, headers=headers, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        response.raise_for_status()
        result = response.json()
        access_token = result['access_token']
        return access_token
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error fetching access token: {str(e)}")

def get_timestamp():
    now = datetime.datetime.now()
    return now.strftime("%Y%m%d%H%M%S")

def initiate_payment(request, amount, phone_number, student_admission_number, transaction_description):
    try:
        access_token = get_access_token()
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

    business_short_code = '222222'
    passkey = 'pass key'
    process_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    callback_url = "callback url"
    timestamp = get_timestamp()
    password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    payload = {
        'BusinessShortCode': business_short_code,
        'Password': password,
        'Timestamp': timestamp,
        'TransactionType': 'CustomerPayBillOnline',
        'Amount': amount,
        'PartyA': phone_number,
        'PartyB': business_short_code,
        'PhoneNumber': phone_number,
        'CallBackURL': callback_url,
        'AccountReference': student_admission_number,
        'TransactionDesc': transaction_description,
    }

    response = requests.post(process_url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return JsonResponse({'success': True, 'message': data})
    else:
        return JsonResponse({'success': False, 'message': 'Payment initiation failed'})

def initiate_ecitizen_payment(request, amount, phone_number, student_admission_number):
    return initiate_payment(request, amount, phone_number, student_admission_number, 'E-Citizen Payment')

def initiate_pocket_money_payment(request, amount, phone_number, student_admission_number):
    return initiate_payment(request, amount, phone_number, student_admission_number, 'Pocket Money Payment')





@csrf_exempt
def mpesa_callback(request):
    if request.method == 'POST':
        payment_data = json.loads(request.body.decode('utf-8'))

        result_code = payment_data['Body']['stkCallback']['ResultCode']
        if result_code == 0:
            callback_metadata = payment_data['Body']['stkCallback']['CallbackMetadata']['Item']
            transaction_id = callback_metadata[1]['Value']
            amount = callback_metadata[0]['Value']
            phone_number = callback_metadata[4]['Value']
            checkout_request_id = payment_data['Body']['stkCallback']['CheckoutRequestID']
            transaction_date = callback_metadata[3]['Value']
            user_email = payment_data.get('user_email', '')

            Payment.objects.create(
                transaction_id=transaction_id,
                phone_number=phone_number,
                amount=amount,
                checkout_request_id=checkout_request_id,
                status='Success',
                transaction_date=transaction_date,
                user_email=user_email
            )

            send_payment_email(user_email, amount, transaction_id, transaction_date)

            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Accepted'})
        else:
            return JsonResponse({'ResultCode': result_code, 'ResultDesc': 'Transaction Failed'})

    return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid Request Method'})

def send_payment_email(user_email, amount, transaction_id, transaction_date):
    if user_email:
        subject = 'Payment Received'
        message = f'Thank you for your payment. \n\n' \
                  f'Amount: {amount}\n' \
                  f'Transaction ID: {transaction_id}\n' \
                  f'Date: {transaction_date}\n\n' \
                  f'We appreciate your business!'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, email_from, recipient_list)

from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login,get_user_model, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from .PaytmChecksum import generate_checksum, verify_checksum
from tray.models import Institute,InstituteMerchantCredentail,Student
import urllib
import uuid
User = get_user_model()

def initiate_payment(request):
    if request.method == "GET":
        return render(request, 'payments/pay.html')
    try:
        user = request.user
        institute = user.student.college
        student = user.student
        institute.identification_token = uuid.uuid4()
        student.identification_token = uuid.uuid4()
        institute.save()
        student.save()
        amount = int(request.POST['amount'])
        print("user___________________",user)
        if user is None:
            raise ValueError
    except:
        return render(request, 'payments/pay.html', context={'error': 'Wrong Account Details or amount'})
    
    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    try:
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
        # request.session['institute_merchant_creds_paytm_secret_key'] = institute_merchant_creds.paytm_secret_key
    except:
        return render(request, 'payments/pay.html', context={'error': 'College has not setup online payments'})
    
    # settings.PAYTM_SECRET_KEY
    merchant_key = institute_merchant_creds.paytm_secret_key
    params = (
        ('MID', institute_merchant_creds.paytm_merchant_id),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(transaction.made_by.email)),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', institute_merchant_creds.paytm_channel_id),
        ('WEBSITE', institute_merchant_creds.paytm_website),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', institute_merchant_creds.paytm_industry_type_id),
        ('CALLBACK_URL', 'http://127.0.0.1:8000/callback/'+ str(institute.identification_token)+ "/"+ str(student.identification_token)),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    try:
        checksum = generate_checksum(paytm_params, merchant_key)
    except ValueError:
        return render(request, 'payments/pay.html', context={'error': 'College has not setup online payments'})
    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'payments/redirect.html', context=paytm_params)


@csrf_exempt
def callback(request,merchant_key,student_key):
    if request.method == 'POST':
        merchant_key_decoded = uuid.UUID(merchant_key).hex
        student_key_decoded = uuid.UUID(student_key).hex
        print("secret key",merchant_key)
        print("secret key decoded",merchant_key_decoded)
        institute = Institute.objects.get(identification_token=merchant_key_decoded)
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
        student = Student.objects.get(identification_token=student_key_decoded)
        paytm_checksum = ''
        print(request.body)
        print(request.POST)
        received_data = dict(request.POST)
        print(received_data)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, institute_merchant_creds.paytm_secret_key, str(paytm_checksum))
        if is_valid_checksum:
            print("Checksum Matched")
            received_data['message'] = "Checksum Matched"
        else:
            print("Checksum Mismatched")
            received_data['message'] = "Checksum Mismatched"
        if received_data.get('MID'):
            mid = received_data.pop('MID')
        if received_data.get('TXNID'):
            txnid = received_data.pop('TXNID')
        if received_data.get('GATEWAYNAME'):
            gateway_name = received_data.pop('GATEWAYNAME')
        if received_data.get('BIN_NAME'):
            bin_name = received_data.pop('BIN_NAME')
        if received_data.get('CHECKSUMHASH'):
            checksum_hash = received_data.pop('CHECKSUMHASH')
        
        print(received_data.get('RESPCODE'))
        if received_data.get('RESPCODE')[0] == '01':
            student.balance += int(float(received_data.get("TXNAMOUNT")[0]))
            student.save()
        return render(request, 'payments/callback.html', context=received_data)





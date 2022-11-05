from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login,get_user_model, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from .PaytmChecksum import generate_checksum, verify_checksum
from tray.models import Institute,InstituteMerchantCredentail,Student,FeePayment
import urllib
import uuid
from django.contrib.auth.decorators import login_required
User = get_user_model()

@login_required
def fee_payment(request):
    if request.method == "GET":
        user = request.user
        institute = user.student.college
        print("institute",institute)
        student = user.student
        print("student",student)
        context ={
            "fee_payment":True,
            "institute":institute
        }
        return render(request, 'payments/pay.html',context)
    user = request.user
    institute = user.student.college
    context ={
            "fee_payment":True,
            "institute":institute
        }
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
        context['error']= 'Wrong Account Details or amount'
        return render(request, 'payments/pay.html', context)
    
    if amount < 1 :
        context['error']= "Amount can't be less than 1 rupee"
        return render(request, 'payments/pay.html', context)
    
    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    try:
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
    except:
        context['error']= 'College has not setup online payments'
        return render(request, 'payments/pay.html', context)
    
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
        ('INDUSTRY_TYPE_ID', institute_merchant_creds.paytm_industry_type),
        ('CALLBACK_URL', settings.RECHARGE_CALLBACK_URL+ "/" + str(institute.identification_token)+ "/"+ str(student.identification_token)+"/fee"),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    print(paytm_params)
    # emi fail code
    # paytm_params['SIMPLIFIED_SUBVENTION']    = {
    #                         "CUSTOMER_ID": str(transaction.made_by.email), #Any unique number identifying a customer
    #                         "SELECT_PLAN_ON_CASHIER_PAGE": "True",
    #                         "SUBVENTION_AMOUNT": "5000000", #Eligible amount for subvention
    #             }
    try:
        checksum = generate_checksum(paytm_params, merchant_key)
    except ValueError:
        return render(request, 'payments/pay.html', context={'error': 'College has not setup online payments'})
    transaction.checksum = checksum
    transaction.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'payments/redirect.html', context=paytm_params)



@login_required
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
    
    if amount < 1 :
        return render(request, 'payments/pay.html', context={'error': "Amount can't be less than 1 rupee"})
    
    transaction = Transaction.objects.create(made_by=user, amount=amount)
    transaction.save()
    try:
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
    except:
        return render(request, 'payments/pay.html', context={'error': 'College has not setup online payments'})
    
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
        ('INDUSTRY_TYPE_ID', institute_merchant_creds.paytm_industry_type),
        ('CALLBACK_URL', settings.RECHARGE_CALLBACK_URL+ "/" + str(institute.identification_token)+ "/"+ str(student.identification_token)+ "/recharge"),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    print(paytm_params)
    # emi fail code
    # paytm_params['SIMPLIFIED_SUBVENTION']    = {
    #                         "CUSTOMER_ID": str(transaction.made_by.email), #Any unique number identifying a customer
    #                         "SELECT_PLAN_ON_CASHIER_PAGE": "True",
    #                         "SUBVENTION_AMOUNT": "5000000", #Eligible amount for subvention
    #             }
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
def callback(request,merchant_token,student_token,payment_type):
    if request.method == 'POST':
        merchant_token_decoded = uuid.UUID(merchant_token).hex
        student_token_decoded = uuid.UUID(student_token).hex
        print("secret key",merchant_token)
        print("secret key decoded",merchant_token_decoded)
        institute = Institute.objects.get(identification_token=merchant_token_decoded)
        institute.identification_token = None
        institute.save()
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
        student = Student.objects.get(identification_token=student_token_decoded)
        student.identification_token = None
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
            print(payment_type)
            if payment_type == "fee":
                FeePayment.objects.create(student=student, institute=institute, paid_fee=int(float(received_data.get("TXNAMOUNT")[0])))
        return render(request, 'payments/callback.html', context=received_data)





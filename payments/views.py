from django.shortcuts import render,redirect
from django.contrib.auth import login as auth_login,get_user_model, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Transaction
from .PaytmChecksum import generate_checksum, verify_checksum
from tray.models import Institute,InstituteMerchantCredentail
User = get_user_model()

def initiate_payment(request):
    if request.method == "GET":
        return render(request, 'payments/pay.html')
    try:
        user = request.user
        institute = user.student.college
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
        ('CALLBACK_URL', 'https://sangeethjoseph.pythonanywhere.com/callback/'),
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
def callback(request):
    if request.method == 'POST':
        try: request.user.student
        except:
            return redirect("home")
        user = request.user
        institute = user.student.college
        institute_merchant_creds = InstituteMerchantCredentail.objects.get(college=institute)
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

        return render(request, 'payments/callback.html', context=received_data)





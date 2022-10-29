from sys import stdout
from django.core.management.base import BaseCommand
from django.utils import timezone
from tray.models import *
from django.db.models import Sum
import razorpay
from django.conf import settings
from datetime import datetime
import time
from dateutil.relativedelta import relativedelta

class Command(BaseCommand):
    help = 'Updates the revenue as addon to the subscription of each institute at the end of each billing cycle'

    def handle(self, *args, **kwargs):
        
        time = timezone.now().strftime('%X')
        self.stdout.write("It's now %s" % time)
        current_datetime = timezone.now()
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        # Attention! Can fetch only upto 100 subscriptions
        self.stdout.write(" Attention! Can fetch only upto 100 subscriptions")
        # fetching all subscriptions
        subscriptions = client.subscription.all({"count":100})
        for subscription in subscriptions["items"]:
            created_at_unix = subscription["created_at"]
            subscription_id = subscription["id"]
            try:
                institute_name = subscription["notes"]["institute"]
            except:
                continue
            try:
                institute = Institute.objects.get(institute_name = institute_name)
            except Institute.DoesNotExist:
                self.stdout.write("can't get institute object from subscription, institute not registered!!")
                self.stdout.write(institute_name)
                continue
            except Institute.MultipleObjectsReturned:
                subscription = Subscription.objects.filter(institute=institute).first()
                self.stdout.write("multiple subscriptions for this college! error!")
                self.stdout.write(institute_name)
            institute_free_trial_expiry_datetime = institute.created_at + relativedelta(months=2)
            subscription_created_at_datetime =  datetime.fromtimestamp(created_at_unix)
            subscription_start_day = subscription_created_at_datetime.day
            
            # updating revenue to subscription only after free trial expiry
            if current_datetime > institute_free_trial_expiry_datetime:
            # condition to find start day of current subscription cycle to add up the revenue
                if current_datetime.day != (subscription_start_day - 1):
                    self.stdout.write("entered if as it is the last day of billing cycle")
                    self.stdout.write(institute.institute_name)
                    previous_month_subscription_cycle_start_datetime = current_datetime.replace(day=subscription_start_day) - relativedelta(months=1)
                    revenues_of_institute_in_current_cycle = Revenue.objects.filter(institute=institute,created_at__gte = previous_month_subscription_cycle_start_datetime, created_at__lte = current_datetime)
                    sum_of_institute_revenues_in_current_cycle = revenues_of_institute_in_current_cycle.aggregate(Sum('day_revenue'))
                    self.stdout.write(str(sum_of_institute_revenues_in_current_cycle['day_revenue__sum']))

                try:
                    # sum_of_institute_revenues_in_current_cycle['day_revenue__sum']
                    rounded_sum_of_institute_revenues_in_current_cycle = round(sum_of_institute_revenues_in_current_cycle.get('day_revenue__sum'),2)
                except:
                    rounded_sum_of_institute_revenues_in_current_cycle = 0
                self.stdout.write(str(rounded_sum_of_institute_revenues_in_current_cycle))
                if str(subscription['payment_method']) != "card":
                    self.stdout.write("payment method:")
                    self.stdout.write(str(subscription['payment_method']))
                    self.stdout.write(institute.institute_name)
                    self.stdout.write("can't add addon as payment is not by card")
                    continue
                if rounded_sum_of_institute_revenues_in_current_cycle < 1:
                    self.stdout.write("no revenue for this institute in current billing cycle")
                    self.stdout.write(institute.institute_name)
                    continue

                # add a condition to skip addon creation if there is an addon already later
                
                response = client.subscription.createAddon(subscription_id, {'item': {
                    'name': 'student revenue',
                    'amount': rounded_sum_of_institute_revenues_in_current_cycle * 100,
                    'currency': 'INR',
                    'description': 'charged at 1 percent of total transactions of student in a day'
                    }, 'quantity': 1})
                self.stdout.write("addon added")
                self.stdout.write(str(response))
            
# tasks.py
from celery import shared_task
from django.utils import timezone
from .models import UserSubscription
from .paymentprocessing import create_payment, execute_payment

@shared_task
def check_due_subscriptions():
    now = timezone.now()
    due_subscriptions = UserSubscription.objects.filter(next_billing_date__lte=now, is_active=True)

    for subscription in due_subscriptions:
        payment = create_payment(subscription)
        if payment and subscription.payer_id:
            if execute_payment(payment.id, subscription.payer_id):
                subscription.next_billing_date = now + timezone.timedelta(days=subscription.subscription_plan.billing_cycle_days)
                subscription.save()
            else:
                subscription.is_active = False
                subscription.save()

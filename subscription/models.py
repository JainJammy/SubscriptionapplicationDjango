from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
# Create your models here.
class SubscriptionPlan(models.Model):
    name=models.CharField(max_length=100)
    description=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    trial_days=models.IntegerField(default=5)
    billing_cycle_days=models.IntegerField(default=30)


    def __str__(self):
        return self.name
    
class UserSubscription(models.Model):
    user=models.ForeignKey(User,on_delete=models.SET_NULL,null=True,related_name="usersubscription")
    subscription_plan=models.ForeignKey("SubscriptionPlan",on_delete=models.SET_NULL,null=True,related_name="Subscription")
    start_date=models.DateTimeField(auto_now_add=True)
    is_active=models.BooleanField(default=False)
    has_trial=models.BooleanField(default=True)
    next_billing_date=models.DateField()
    """Paypal Payer id saving in the database"""
    payer_id = models.CharField(max_length=255, null=True, blank=True) 
    billing_agreement_id = models.CharField(max_length=255, null=True, blank=True)  # New field
    start_date = models.DateTimeField(auto_now_add=True)

"""Many to Many relationship between User model and Subscription"""

User.add_to_class('subscriptions',models.ManyToManyField(SubscriptionPlan,through=UserSubscription))
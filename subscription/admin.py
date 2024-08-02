from django.contrib import admin
from .models import *
# Register your models here.
"""For admin"""
@admin.register(SubscriptionPlan)
class SusbscriptionAdmin(admin.ModelAdmin):
    list_display=['name','description','price','trial_days','billing_cycle_days']
    search_fields=('name','description')

@admin.register(UserSubscription)

class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display=['user','subscription_plan','start_date','is_active','has_trial','next_billing_date']
    search_fields=('user__username','subscription_plan__name')
    list_filter=('is_active','has_trial','start_date')
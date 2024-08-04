from django.shortcuts import render,HttpResponseRedirect
from .forms import SignupForm
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,redirect
from django.views.decorators.csrf import csrf_exempt
from subscription.models import *
from datetime import timedelta
from datetime import datetime
from django.utils import timezone
import paypalrestsdk
from django.conf import settings
from django.http import HttpResponseBadRequest
# Create your views here.
paypalrestsdk.configure({
    "mode":settings.PAYPAL_MODE,
    "client_id":settings.PAYPAL_CLIENT_ID,
    "client_secret":settings.PAYPAL_SECRET_ID
})

def authView(request):
    if request.method == "POST":
        form=SignupForm(request.POST)
        if form.is_valid():
            messages.success(request,"Account Created Successfully")
            form.save()
    else:    
        form=SignupForm()
    return render(request,"signup.html",context={"form":form})


def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            fm=AuthenticationForm(request=request,data=request.POST)
            if fm.is_valid():
                uname=fm.cleaned_data["username"]
                upass=fm.cleaned_data["password"]
                user=authenticate(username=uname,password=upass)
                if user is not None:
                    login(request,user)
                    messages.success(request,"Logged in successfully")
                    return HttpResponseRedirect("/profile/")

        else:            
           fm=AuthenticationForm()
        return render(request,'login.html',{'form':fm})
    else:
        return HttpResponseRedirect("/profile/")

#@login_required
def user_profile(request):
    if request.user.is_authenticated:
       user_subscriptions=UserSubscription.objects.filter(user=request.user)
       subscriptions = []
       for subscription in user_subscriptions:
           trial_end_date = subscription.start_date + timedelta(days=subscription.subscription_plan.trial_days)
           days_left_in_trial = (trial_end_date - timezone.now()).days
           is_trial = days_left_in_trial > 0
           subscriptions.append({
            'subscription': subscription,
            'is_trial': is_trial,
            'days_left_in_trial': max(0,days_left_in_trial),
            'is_active':subscription.is_active,
            'next_billing_date':subscription.next_billing_date
        })

       context = {
        'name': request.user.username,
        'subscriptions': subscriptions,
       }
       return render(request,"profile.html",context)
    else:
        return HttpResponseRedirect("/login/")
#@login_required    
"""def subscribe(request,subscription_plan_id):
    #import pdb
    #pdb.set_trace()
    if request.user.is_authenticated:
        if request.method == "POST":
           subscription_plan=SubscriptionPlan.objects.get(id=subscription_plan_id)
           print(subscription_plan)
           billing_plan = paypalrestsdk.BillingPlan({
              "name": f"{subscription_plan.name} Plan",
               "description": f"Subscription plan for {subscription_plan.name}",
               "type": "fixed",
                "payment_definitions": [{
                "name": "Regular Payments",
                "type": "REGULAR",
                "frequency": "MONTH",
                "frequency_interval": "1",
                "amount": {
                 "value": str(subscription_plan.price),
                 "currency": "USD"
                  },
                  "cycles": "0",  # 0 means infinite cycles
                  "charge_models": []
                  }],
                 "merchant_preferences": {
                 "setup_fee": {
                "value": "0",
                "currency": "USD"
                 },
                "cancel_url": request.build_absolute_uri('/paypal_cancel/'),
                "return_url": request.build_absolute_uri('/auto_return/'),
                "auto_bill_amount": "YES",
                "initial_fail_amount_action": "CONTINUE",
                "max_fail_attempts": "1"
                } 
                })
           if billing_plan.create() and billing_plan.activate():
              # Create Billing Agreement
              start_date = (datetime.now() + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
              billing_agreement = paypalrestsdk.BillingAgreement({
              "name": f"{subscription_plan.name} Agreement",
              "description": f"Agreement for {subscription_plan.name} plan",
              "start_date": start_date,
               "plan": {
                    "id": billing_plan.id
                },
                "payer": {
                    "payment_method": "paypal"
                }
               })     
           if billing_agreement.create():
               for link in billing_agreement.links:
                   if link.rel == "approval_url":
                      approval_url = link.href
                      return redirect(approval_url)
           else:
                 return HttpResponseBadRequest("Bad Request Billing request")
     
           return render(request, 'subscribe.html', {'subscription_plan': subscription_plan})
    else:
        return HttpResponseRedirect("/login/")"""

def create_billing_plan(subscription):
    billing_plan = paypalrestsdk.BillingPlan({
        "name": f"{subscription.name} Plan",
        "description": f"Monthly subscription plan for {subscription.name}",
        "type": "fixed",
        "payment_definitions": [{
            "name": "Regular Payments",
            "type": "REGULAR",
            "frequency": "DAY",
            "frequency_interval": "1",
            "amount": {
                "value": str(subscription.price),
                "currency": "USD"
            },
            "cycles": "12",
            "charge_models": []
        }],
        "merchant_preferences": {
            "setup_fee": {
                "value": "0",
                "currency": "USD"
            },
            "cancel_url": "http://127.0.0.1:8000/paypal_cancel/",
            "return_url": "http://127.0.0.1:8000/paypal_auto_return/",
            "auto_bill_amount": "YES",
            "initial_fail_amount_action": "CONTINUE",
            "max_fail_attempts": "1"
        }
    })
    if billing_plan.create():
        if billing_plan.activate():
            return billing_plan
        else:
            print(billing_plan.error)
            return None
    else:
        print(billing_plan.error)
        return None
        
def create_billing_agreement(user_subscription,subscription_plan,plan_id):
    #import pdb
    #pdb.set_trace()
    #i#mport pdb
    #pdb.set_trace()
    #start_date = user_subscription.next_billing_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    start_date = (datetime.utcnow() + timedelta(minutes=1)).strftime('%Y-%m-%dT%H:%M:%SZ')
    #start_date = (user_subscription.next_billing_date + timedelta(minutes=5)).strftime('%Y-%m-%dT%H:%M:%SZ')
    #start_date=datetime.now()+timedelta(minutes=5)
    billing_agreement = paypalrestsdk.BillingAgreement({
        "name": f"{subscription_plan.name} Agreement",
        "description": f"Agreement for {subscription_plan.name} plan",
        "start_date": start_date,
        "plan": {
            "id": plan_id
        },
        "payer": {
            "payment_method": "paypal"
        }
    })
    if billing_agreement.create():
        for link in billing_agreement.links:
            if link.rel == "approval_url":
                approval_url = link.href
                print(f"Redirect user to {approval_url}")
                return approval_url
    else:
        print(billing_agreement.error)
        return None


def subscribe(request, subscription_plan_id):
    if request.user.is_authenticated:
       if request.method == "POST":
          subscription_plan = SubscriptionPlan.objects.get(id=subscription_plan_id)
          print(subscription_plan)
          # Create the billing plan
          billing_plan = create_billing_plan(subscription_plan)
          if billing_plan:
             user_subscription = UserSubscription.objects.get(user=request.user, subscription_plan=subscription_plan)
             next_billing_date = user_subscription.next_billing_date
             approval_url = create_billing_agreement(user_subscription,subscription_plan,billing_plan.id)
             if approval_url:
                 print("subscription id",subscription_plan.id)
                 request.session['subscription_plan_id'] = subscription_plan.id
                 return redirect(approval_url)
             else:
                    return HttpResponseBadRequest("Failed to create billing agreement")
          else:
                return HttpResponseBadRequest("Failed to create billing plan")
       else:  
        subscription_plan = SubscriptionPlan.objects.get(id=subscription_plan_id)
        print(subscription_plan)
        return render(request, "subscribe.html", {"subscription_plan": subscription_plan})

    else:
        return HttpResponseRedirect("/login/")

def paypal_cancel(request):
    return  render(request, 'payment_cancelled.html')

def execute_agreement(token):
    billing_agreement = paypalrestsdk.BillingAgreement.execute(token)
    if billing_agreement.state == "Active":
        return billing_agreement
    else:
        print(billing_agreement.error)
        return None


@csrf_exempt
def auto_return(request):
    #import pdb
    #pdb.set_trace()
    token = request.GET.get('token')
    if token:
        billing_agreement = paypalrestsdk.BillingAgreement.execute(token)
        if billing_agreement.state == "Active":
           payer_id = billing_agreement.payer.payer_info.payer_id
           billing_agreement_id = billing_agreement.id 
           print(request)
           subscription_plan_id = request.session.get('subscription_plan_id')
           print("Subscription",subscription_plan_id)
           if not subscription_plan_id:
                return HttpResponseBadRequest("Subscription plan not found in session")
           try:
                subscription_plan = SubscriptionPlan.objects.get(id=subscription_plan_id)
           except SubscriptionPlan.DoesNotExist:
                return HttpResponseBadRequest("Subscription plan does not exist")


           # Find the user's subscription and update it
           user_subscription = UserSubscription.objects.filter(user=request.user,id=subscription_plan_id).first()
           user_subscription.payer_id = payer_id
           user_subscription.billing_agreement_id = billing_agreement_id
           user_subscription.next_billing_date = datetime.now() + timedelta(days=30)  # Set the next billing date
           user_subscription.save()
           subscription_plan = user_subscription.subscription_plan
           payment = paypalrestsdk.Payment({
                    "intent": "sale",
                    "payer": {
                        "payment_method": "paypal"
                    },
                    "redirect_urls": {
                        "return_url": settings.PAYPAL_RETURN_URL,
                        "cancel_url": settings.PAYPAL_CANCEL_URL
                    },
                    "transactions": [
                        {
                            "item_list": {
                                "items": [{
                                    "name": subscription_plan.name,
                                    "sku": f"sub_{subscription_plan.id}",
                                    "price": str(subscription_plan.price),
                                    "currency": "USD",
                                    "quantity": 1
                                }]
                            },
                            "amount": {
                                "total": str(subscription_plan.price),
                                "currency": "USD"
                            },
                            "description": f"Subscription to {subscription_plan.name}"
                        }
                    ]
                })

           if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                       approval_url = link.href
                       break
                return redirect(approval_url)
           else:
                return HttpResponseBadRequest("Payment creation failed")
        else:
            return HttpResponseBadRequest("Billing state not active")

"""PayPal will send the POST request"""

@csrf_exempt
def paypal_return(request):
    print("view hitted................................")
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        subscription_plan_id = payment.transactions[0].item_list.items[0].sku.split('_')[-1] 
        subscription_plan = SubscriptionPlan.objects.get(id=subscription_plan_id)
        existing_subscription = UserSubscription.objects.filter(user=request.user, subscription_plan=subscription_plan).last()
        if existing_subscription:
            existing_subscription.is_active=True
            existing_subscription.start_date=timezone.now()
            existing_subscription.next_billing_date=timezone.now()+timedelta(days=subscription_plan.billing_cycle_days)
            existing_subscription.has_trial=False
            existing_subscription.payer_id=payer_id
            existing_subscription.save()
        return HttpResponseRedirect("/profile/")
    else:
        #print(payment.error)
        return render(request,"payment_failed.html",{"payment":payment})

#@login_required
def cancel_subscription(request,id):
    if request.user.is_authenticated:
        subscription=UserSubscription.objects.filter(id=id,user=request.user).last()
        if request.method == "POST":
            subscription.is_active=False
            subscription.save()
            return redirect("profile")
    else:
        return HttpResponseRedirect("/login/")



def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


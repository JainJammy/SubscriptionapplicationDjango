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
def subscribe(request,subscription_plan_id):
    #import pdb
    #pdb.set_trace()
    if request.user.is_authenticated:
        subscription_plan=SubscriptionPlan.objects.get(id=subscription_plan_id)
        if request.method == "POST":
            """"Paypal Payload structure"""
            #https://developer.paypal.com/docs/api/payments/v1/
            payment=paypalrestsdk.Payment({
                "intent":"sale",
                "payer":{
                    "payment_method":"paypal"
                },
                "redirect_urls":{
                    "return_url":settings.PAYPAL_RETURN_URL,
                    "cancel_url":settings.PAYPAL_CANCEL_URL
                },
                "transactions":[
                    {
                        "item_list":{
                            "items":[{
                                "name":subscription_plan.name,
                                "sku":f"sub_{subscription_plan_id}",
                                "price":str(subscription_plan.price),
                                "currency":"USD",
                                "quantity":1
                                
                            }]
                        },
                        "amount":{
                            "total":str(subscription_plan.price),
                            "currency":"USD"
                        },
                        "description":f"Subscription to {subscription_plan.name}"
                    }
                ]

            })

            if payment.create():
                for link in payment.links:
                    if link.rel == "approval_url":
                        approval_url=link.href
                        break
                return redirect(approval_url)
            else:
                return HttpResponseBadRequest("Payment creation failed")
        return render(request, 'subscribe.html', {'subscription_plan': subscription_plan})
    else:
        return HttpResponseRedirect("/login/")
def paypal_cancel(request):
    return render(request, 'payment_cancelled.html')

"""PayPal will send the POST request"""
@csrf_exempt
def paypal_return(request):
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


import paypalrestsdk
from django.conf import settings

paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,  # 'sandbox' or 'live'
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_SECRET_ID
})

def create_payment(subscription):
    print("Payment,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,")
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": subscription.subscription_plan.name,
                    "sku": f"sub_{subscription.subscription_plan.id}",
                    "price": str(subscription.subscription_plan.price),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(subscription.subscription_plan.price),
                "currency": "USD"
            },
            "description": f"Subscription to {subscription.subscription_plan.name}"
        }]
    })

    if payment.create():
        return payment
    else:
        print(payment.error)
        return None

def execute_payment(payment_id, payer_id):
    payment = paypalrestsdk.Payment.find(payment_id)
    if payment.execute({"payer_id": payer_id}):
        return True
    else:
        print(payment.error)
        return False

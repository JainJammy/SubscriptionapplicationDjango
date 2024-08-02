from django.contrib import admin
from django.urls import path,include
from subscription import views
urlpatterns = [
    #path('admin/', admin.site.urls)
    path("",views.user_profile,name="profile"),
    path("signup/",views.authView,name="signup"),
    path("login/",views.user_login,name="login"),
    path("profile/",views.user_profile,name="profile"),
    path("logout/",views.user_logout,name="logout"),
    path('subscribe/<int:subscription_plan_id>/', views.subscribe, name='subscribe'),
    path("cancel_subscription/<int:id>/",views.cancel_subscription,name="cancel_subscription"),
    path("paypal_return/",views.paypal_return,name="paypal_return"),
    path("paypal_cancel/",views.paypal_cancel,name="paypal_cancel")    

]

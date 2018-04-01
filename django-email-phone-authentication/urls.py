"""forfilm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_auth.registration.views import VerifyEmailView

from authentication import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('login/', views.LoginView.as_view(), name='account_login'),
    path('', include('rest_auth.urls')),
    path('registration/', views.RegisterView.as_view(), name='account_signup'),
    path('registration/', include('rest_auth.registration.urls')),

    re_path(r'^account-confirm-email/sent', views.django_rest_auth_null,
            name='account_email_verification_sent'),
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', VerifyEmailView.as_view(),
            name='account_confirm_email'),

    path('verify-phone-number/', views.VerifyPhoneView.as_view()),
]

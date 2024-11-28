from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('signin', Signin.as_view(), name='signin'),
    path('signin_otp', Otpsignin.as_view(), name='signin_otp'),
    path("signin_otp_resend", OtpsigninResend.as_view(), name="signin_otp_resend"),
    path('elector_code_verification', ElectorCodeVerification.as_view(), name='elector_code_verification'),
    path('signup_otp', OtpSignup.as_view(), name="signup_otp"),
    path('signup', Signup.as_view(), name="signup"),
    path("forgot_password", ForgotPassword.as_view(), name="forgot_password"),
    path("reset_password", ResetPassword.as_view(), name="reset_password"),
    path('logout', deconnexion, name='deconnexion'),
]
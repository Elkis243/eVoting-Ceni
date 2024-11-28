from django.shortcuts import redirect
from functools import wraps
from django.contrib import messages

def otp_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        email = request.session.get('email')
        totp_secret = request.session.get('totp_secret')
        validity_time_string = request.session.get('validity_time_string')
        
        if email and totp_secret and validity_time_string:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Authentification requise. Veuillez essayer de vous reconnecter !")
            return redirect('signin')

    return _wrapped_view

def national_number_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        national_number = request.session.get('national_number')

        if national_number:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Numéro national requis. Veuillez réessayer !")
            return redirect("elector_code_verification")
    return _wrapped_view
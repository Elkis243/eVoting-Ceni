from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
import pyotp
from datetime import datetime, timedelta
from .tasks import *
from django.utils.decorators import method_decorator
from eVoting_Ceni.decorators import *
from elector.models import *
from administration.models import *
from eVoting_Ceni.utils import *
from django.db import transaction
import logging
from django.contrib.auth.decorators import login_required

logger = logging.getLogger("my_logger")

def home(request):
    return render(request, 'home.html')

class Signin(View):
    def get(self, request):
        return render(request, 'users/signin.html')

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)
        if user is not None:
            if user.user_type != 'admin' and user.user_type != 'elector':
                logger.error(f"Erreur de connexion : Tentative d'intrusion détectée pour l'utilisateur de type {user.user_type} avec l'email {user.email}, IP {request.META.get('REMOTE_ADDR')}")
                messages.error(request, "Adresse email ou mot de passe incorrect !")
                return redirect("signin")
            else:
                totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
                totp_secret = totp.secret
                validity_time = datetime.now() + timedelta(minutes=5)
                
                request.session["email"] = email
                request.session["totp_secret"] = totp_secret
                request.session["validity_time_string"] = str(validity_time)
                
                send_otp.delay(totp_secret, email)
                return redirect('signin_otp')
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect !")
            return redirect("signin")

class Otpsignin(View):
    @method_decorator(otp_session_required)
    def get(self, request):
        return render(request, "users/otp.html")

    def post(self, request):
        otp = request.POST.get("otp")
        
        email = request.session.get("email")
        totp_secret = request.session.get("totp_secret")
        validity_time_string = request.session.get("validity_time_string")

        if not (email and totp_secret and validity_time_string):
            logger.error("Échec de la vérification de l'OTP. Une ou plusieurs variables requises sont vides : 'email', 'totp_secret', ou 'validity_time_string'.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")
        
        try:
            validity_time = datetime.fromisoformat(validity_time_string)
        except ValueError:
            logger.error("Le format de la date d'expiration est invalide.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin_otp")
        
        if validity_time <= datetime.now():
            messages.error(request, "Votre code de confirmation a expiré. Veuillez demander un nouveau code !")
            return redirect("signin_otp")

        totp = pyotp.TOTP(totp_secret, interval=300)
        if not totp.verify(otp):
            messages.error(request, "Le code de confirmation que vous avez entré est invalide. Veuillez vérifier et réessayer !")
            return redirect("signin_otp")

        try:
            user = get_object_or_404(User, email=email)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            del request.session["email"]
            del request.session["totp_secret"]
            del request.session["validity_time_string"]

            if user.user_type == "admin":
                return redirect("election")
            elif user.user_type == "elector":
                return redirect("list_candidate")
        except User.DoesNotExist as e:
            logger.error(f"Utilisateur avec l'email {email} n'existe pas.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")
        except Exception as e:
            logger.error(f"Erreur lors de la confirmation de l'OTP : {e}")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")

class OtpsigninResend(View):
    @method_decorator(otp_session_required)
    def get(self, request):
        email = request.session.get("email")
        
        if not email:
            logger.error("Échec lors du réenvoi de l'OTP. Une variable requise est manquante : 'email'.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")

        totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
        totp_secret = totp.secret
        validity_time = datetime.now() + timedelta(minutes=5)
        
        request.session["totp_secret"] = totp_secret
        request.session["validity_time_string"] = str(validity_time)
        
        send_otp.delay(totp_secret, email)
        return redirect("signin_otp")

class ForgotPassword(View):
    def get(self, request):
        return render(request, 'users/forgot_password.html')

    def post(self, request):
        email = request.POST.get("email")
        
        if User.objects.filter(email=email).exists():
            totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
            totp_secret = totp.secret
            validity_time = datetime.now() + timedelta(minutes=5)
            request.session["email"] = email
            request.session["totp_secret"] = totp_secret
            request.session["validity_time_string"] = str(validity_time)
            send_otp.delay(totp_secret, email)
            return redirect("reset_password")
        else:
            messages.error(request, "Adresse email introuvable dans le système !")
            return redirect("forgot_password")
        
class ResetPassword(View):
    @method_decorator(otp_session_required)
    def get(self, request):
        return render(request, 'users/reset_password.html')

    def post(self, request):
        otp = request.POST.get("otp")
        
        email = request.session.get("email")
        totp_secret = request.session.get("totp_secret")
        validity_time_string = request.session.get("validity_time_string")

        if not (email and totp_secret and validity_time_string):
            logger.error("Échec de la vérification de l'OTP. Une ou plusieurs variables requises sont vides : 'email', 'totp_secret', ou 'validity_time_string'.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")

        try:
            validity_time = datetime.fromisoformat(validity_time_string)
        except ValueError:
            logger.error("Le format de la date d'expiration est invalide.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")
        
        if validity_time <= datetime.now():
            messages.error(request, "Votre code de confirmation a expiré. Veuillez demander un nouveau code !")
            return redirect("signin")

        totp = pyotp.TOTP(totp_secret, interval=300)
        if not totp.verify(otp):
            messages.error(request, "Le code de confirmation que vous avez entré est invalide. Veuillez vérifier et réessayer !")
            return redirect("signin")

        try:
            user = get_object_or_404(User, email=email)
            password = generate_random_password()
            user.set_password(password)
            user.save()
            send_password.delay(password, user.email)
            messages.success(request, "Votre mot de passe a été réinitialisé avec succès. Un nouveau mot de passe a été envoyé à votre adresse email !")
            return redirect("signin")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation du mot de passe : {e}")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("signin")

class ElectorCodeVerification(View):
    def get(self, request):
        created_election_exist = Election.objects.filter(status='created').exists()
        return render(request, 'users/elector_code_verification.html', {
            'created_election_exist': created_election_exist
        })

    def post(self, request):
        national_number = hash_message(request.POST.get("national_number"))
        
        created_election = Election.objects.filter(status='created').first()
        if ElectoralList.objects.filter(national_number=national_number).exists():
            get_elector = ElectoralList.objects.get(national_number=national_number)
            email = get_elector.email
            
            try:
                elector = Elector.objects.get(national_number=national_number)
                if created_election.electors.filter(pk=elector.pk).exists():
                    messages.error(request, "L'électeur est déjà inscrit à cette élection !")
                    return redirect("elector_code_verification")
                else:
                    return self.elector_code_otp(request, national_number, email)
            except Elector.DoesNotExist:
                return self.elector_code_otp(request, national_number, email)
        else:
            messages.error(request, "L'électeur n'est pas inscrit dans la liste électorale !")
            return redirect('elector_code_verification')
        
    def elector_code_otp(self, request, national_number, email):
        totp = pyotp.TOTP(pyotp.random_base32(), interval=300)
        totp_secret = totp.secret
        validity_time = datetime.now() + timedelta(minutes=5)
        
        request.session["national_number"] = national_number
        request.session["totp_secret"] = totp_secret
        request.session["validity_time_string"] = str(validity_time)
        
        send_otp.delay(totp_secret, email)
        return redirect("signup_otp")
        
class OtpSignup(View):
    @method_decorator(national_number_required)
    def get(self, request):
        return render(request, 'users/signup_otp.html')
    
    def post(self, request):
        otp = request.POST.get("otp")
        
        totp_secret = request.session.get("totp_secret")
        validity_time_string = request.session.get("validity_time_string")
        national_number = request.session.get("national_number")
        
        if not (national_number and totp_secret and validity_time_string):
            logger.error("Échec de la vérification de l'OTP. Une ou plusieurs variables requises sont vides : 'email', 'totp_secret', ou 'validity_time_string'.")
            messages.error(request, "Une erreur inattendue s'est produite. Veuillez ressayer !")
            return redirect("elector_code_verification")
        
        try:
            validity_time = datetime.fromisoformat(validity_time_string)
        except ValueError:
            logger.error("Le format de la date d'expiration est invalide.")
            messages.error(request, "Nous avons rencontré un problème lors de la confirmation de l'OTP. Veuillez réessayer dans un instant !")
            return redirect("elector_code_verification")
        
        if validity_time <= datetime.now():
            messages.error(request, "Votre code de confirmation a expiré. Veuillez demander un nouveau code !")
            return redirect("elector_code_verification")
        
        totp = pyotp.TOTP(totp_secret, interval=300)
        if not totp.verify(otp):
            messages.error(request, "Le code de confirmation que vous avez entré est invalide. Veuillez vérifier et réessayer !")
            return redirect("signup_otp")
        
        return redirect('signup')

class Signup(View):
    @method_decorator(national_number_required)
    def get(self, request):
        created_election = Election.objects.filter(status='created').first()
        if not created_election:
            messages.error(request, "Aucune élection créée trouvée !")
            return redirect("signin")
        
        national_number = request.session.get("national_number")
        if not national_number:
            messages.error(request, "Le numéro national est requis !")
            return redirect("elector_code_verification")
        
        try:
            get_list = ElectoralList.objects.get(national_number=national_number, election=created_election)
            email = get_list.email
            country = get_list.country
            password = generate_random_password()
            
            elector = Elector.objects.get(national_number=national_number)
            if not created_election.electors.filter(pk=elector.pk).exists():
                with transaction.atomic():
                    elector.email = email
                    elector.country = country
                    elector.set_password(password)
                    elector.save()
                    
                    created_election.electors.add(elector)
                    created_election.save()
                    del request.session["national_number"]
                    send_password.delay(password, email)
                    messages.success(request, "Félicitations, votre inscription est réussie, consultez votre email pour découvrir votre mot de passe !")
                    return redirect("signin")
        except Elector.DoesNotExist as e:
            with transaction.atomic():
                elector = Elector.objects.create(
                        email=email,
                        user_type='elector',
                        national_number=national_number,
                        country=country,
                )
                elector.set_password(password)
                elector.save()
                
                created_election.electors.add(elector)
                created_election.save()
                del request.session["national_number"]
                send_password.delay(password, email)
                messages.success(request, "Félicitations, votre inscription est réussie, consultez votre email pour découvrir votre mot de passe !")
                return redirect('signin')
        except ElectoralList.DoesNotExist as e:
            logger.error(f"Erreur : Le fichier électoral est introuvable. Détails : {e}")
            messages.error(request, "Une erreur inattendue s'est produite !")
            return redirect("elector_code_verification")
        except Exception as e:
            logger.error(f"Une erreur est inattendue s'est produite : {e}")
            messages.error(request, "Une erreur inattendue s'est produite !")
            return redirect("signup")

def deconnexion(request):
    logout(request)
    request.session.flush()
    return redirect("signin")

def page404(request, exception):
    return render(request, 'users/404.html')
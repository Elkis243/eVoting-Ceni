from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from administration.models import *
from django.contrib import messages
import logging
from django.db.models import *
from django.db.models.functions import Coalesce
from eVoting_Ceni.utils import *
from .models import *
from users.tasks import *
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

logger = logging.getLogger("my_logger")

class ListCandidate(View):
    def get(self, request):
        active_election_exist = Election.objects.filter(status="active").exists()
        candidates = Candidate.objects.filter(election__status="active")
        voted = False

        if request.user.is_authenticated:
            try:
                elector = get_object_or_404(Elector, pk=request.user.pk)
                elector_token = encrypt_message(elector.elector_token)
                election = Election.objects.filter(status="active").first()

                if election:
                    is_voted = Vote.objects.filter(elector_token=elector_token).exists()
                    voted = is_voted
                    if voted:
                        try:
                            vote = Vote.objects.get(elector_token=elector_token)
                            timestamp = vote.timestamp
                        except Exception as e:
                            logger.error(f"Le vote n'existe pas : {e}")
                            messages.error(request, "Une erreur inattendue s'est produite !")
                            return redirect('signin')
                    else:
                        timestamp = None
                else:
                    timestamp = None
            except Elector.DoesNotExist as e:
                logger.error(f"L'electeur n'existe pas : {e}")
                messages.error(request, "Une erreur inattendue s'est produite !")
                return redirect("signin")
        else:
            logger.error(f"Authentification requise.")
            messages.error(request, "Authentification requise !")
            return redirect("signin")
        return render(request, 'elector/vote.html',{
                "name": "list_candidate",
                'election':election,
                "active_election_exist": active_election_exist,
                "candidates": candidates,
                "voted": voted,
                'timestamp':timestamp,
            },
        )
        
class ChoiceCandidate(View):
    def get(self, request, pk):
        if not request.user.is_authenticated:
            messages.error(request, "Authentification requise !")
            return redirect("signin")
        
        try:
            election = Election.objects.filter(status="active").first()
            if not election:
                messages.error(request, "Aucune élection active n'a été trouvée !")
                return redirect("list_candidate")
            
            elector = get_object_or_404(Elector, pk=request.user.pk)
            candidate = get_object_or_404(Candidate, pk=pk)

            vote = Vote.objects.create(
                elector_token=elector.elector_token,
                candidate_token=candidate.candidate_token,
                election=election,
                country=elector.country
            )
            elector_token = vote.elector_token
            elector_token_hex = elector_token.hex()
            encrypt_elector_token = encrypt_message(elector_token_hex) 
            vote_evidence = encrypt_elector_token.hex()
            send_vote_evidence.delay(vote_evidence, request.user.email)
            return redirect("list_candidate")
        except Exception as e:
            logger.error(f"Erreur lors du vote : {e}")
            messages.error(request, "Une erreur inattendue s'est produite. Veuillez réessayer.")
            return redirect("list_candidate")

class ChoiceWhiteVote(View):
    def get(self, request):
        if not request.user.is_authenticated:
            messages.error(request, "Authentification requise !")
            return redirect("signin")
        
        try:
            election = Election.objects.filter(status="active").first()
            
            if not election:
                messages.error(request, "Aucune élection active trouvée !")
                return redirect("list_candidate")
            
            elector = get_object_or_404(Elector, pk=request.user.pk)
            vote = Vote.objects.create(
                elector_token=elector.elector_token,
                election=election,
                country=elector.country,
                is_blank=True
            )
            
            elector_token = vote.elector_token
            elector_token_hex = elector_token.hex()
            encrypt_elector_token = encrypt_message(elector_token_hex) 
            vote_evidence = encrypt_elector_token.hex()
            send_vote_evidence.delay(vote_evidence, request.user.email)
            return redirect("list_candidate")
        except Exception as e:
            logger.error(f"Erreur lors du vote blanc : {e}")
            messages.error(request, "Une erreur inattendue s'est produite. Veuillez réessayer.")
            return redirect("list_candidate")

@login_required
def history(request):
    elections = Election.objects.filter(status='published')
    return render(request, 'elector/history.html', {
        'name': 'history',
        'elections':elections
    })

@login_required
def view_result(request, pk):
    try:
        election = get_object_or_404(Election, pk=pk)
        candidates = Candidate.objects.filter(election=election)
        candidates_exist = candidates.exists()
        if election.status == "published":
            total_votes = Vote.objects.filter(election=election, is_valid=True, is_counted=True).count()
            total_invalid_votes = Vote.objects.filter(election=election, is_valid=False, is_counted=True).count()
            total_blank_votes = Vote.objects.filter(election=election, is_blank=True, is_counted=True).count()
            
            count_electoral_list = ElectoralList.objects.all().count()
            electors_count = election.electors_count
            global_votes = Vote.objects.filter(election=election).count()
            participation_rate = (global_votes * 100) / count_electoral_list if count_electoral_list > 0 else 0
            
            resultat_pourcentage = calculer_resultats(request, election, Vote, Candidate)
            votes_pays = decompte_votes_par_pays(election, Vote, Candidate)

        else:
            total_votes = 0
            total_blank_votes = 0
            participation_rate = 0
            total_invalid_votes = 0
            resultat_pourcentage = []
            votes_pays = []
    except Election.DoesNotExist as e:
        logger.error(f"L'élection n'existe pas : {e}")
        messages.error(request, "Une erreur inattendue s'est produite !")
        return redirect("list_candidate")
    return render(request, "elector/view_result.html", {
        "name": "history",
        "election": election,
        "candidates_exist": candidates_exist,
        "candidates": candidates,
        'total_votes': total_votes,
        'participation_rate': participation_rate,
        'total_blank_votes': total_blank_votes,
        'total_invalid_votes': total_invalid_votes,
        'resultat_pourcentage': resultat_pourcentage,
        'votes_pays': votes_pays
    })

@login_required
def verify(request):
    elections = Election.objects.filter(status="published")

    if request.method == 'POST':
        vote_evidence = request.POST.get('vote_evidence')
        election_pk = request.POST.get('election')

        if not vote_evidence or not election_pk:
            messages.error(request, "Les informations de vote ou d'élection sont manquantes !")
            return redirect('verify')
        try:
            vote_evidence_byte = bytes.fromhex(vote_evidence)
            decrypt_data = decrypt_message(vote_evidence_byte)
            decrypt_data_byte = bytes.fromhex(decrypt_data)
        except ValueError:
            messages.error(request, "Le code de référence de vote est invalide !")
            return redirect('verify')
        except Exception as e:
            logger.error(f"Une erreur s'est produite {e}")
            messages.error(request, "Une erreur s'est produite lors du traitement du code de référence de vote !")
            return redirect('verify')
        try:
            election = Election.objects.get(pk=election_pk)
        except Election.DoesNotExist as e:
            logger.error(f"L'élection n'existe pas : {e}")
            messages.error(request, "Une erreur s'est produite lors du traitement du code de référence de vote !")
            return redirect('verify')

        if Vote.objects.filter(elector_token=decrypt_data_byte, election=election).exists():
            messages.success(request, f"Votre vote a été comptabilisé avec succès. Merci de contribuer au processus démocratique !")
        else:
            messages.error(request, f"Nous sommes désolés, mais nous n'avons pas pu enregistrer votre vote. Veuillez vérifier vos informations d'identification pour l'{election}' ou contacter notre support technique pour plus d'informations.")
    return render(request, 'elector/verify.html', {
        'name': 'verify',
        'elections': elections
    })

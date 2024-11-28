import random
import string
import hashlib
from django.conf import settings
from datetime import datetime
import zoneinfo
import tzlocal
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from django.db.models import Count
from django.contrib import messages
from django.shortcuts import redirect

def generate_random_password(length=10):
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def hash_message(message):
    encrypt_message = (message + settings.HASH_SALT).encode('utf-8')
    return hashlib.sha256(encrypt_message).hexdigest()

def encrypt_message(message):
    key = bytes.fromhex(settings.ENCRYPTION_KEY)
    iv = bytes.fromhex(settings.ENCRYPTION_IV)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(message.encode()) + encryptor.finalize()
    return encrypted_message

def decrypt_message(encrypted_message):
    key = bytes.fromhex(settings.ENCRYPTION_KEY)
    iv = bytes.fromhex(settings.ENCRYPTION_IV)
    cipher = Cipher(algorithms.AES(key), modes.CFB(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_message) + decryptor.finalize()
    return decrypted_message.decode()

def calculer_resultats(request, election, Vote, Candidate):
    votes = Vote.objects.filter(election=election, is_valid=True, is_counted=True) \
        .values('candidate_token') \
        .annotate(count_votes=Count('id')) \
        .order_by('-count_votes')
    candidats = Candidate.objects.filter(election=election)
    resultat = {}
    for candidat in candidats:
        resultat[(candidat.first_name, candidat.last_name, candidat.name, candidat.picture.url )] = 0

    for vote in votes:
        candidate_token = decrypt_message(vote['candidate_token'])
        count_votes = vote['count_votes']
        try:
            candidat = Candidate.objects.get(candidate_token=candidate_token)
            resultat[(candidat.first_name, candidat.last_name, candidat.name, candidat.picture.url if candidat.picture else None)] = count_votes
        except Candidate.DoesNotExist as e:
            messages.error(request, f"Une erreur inattendue s'est produite ! {e}")
            return redirect("election")
        
    total_votes = sum(resultat.values())

    resultat_pourcentage = [
        {
            'first_name': first_name,
            'last_name': last_name,
            'name': name,
            'picture_url': picture_url,
            'votes': votes,
            'percentage': (votes / total_votes) * 100 if total_votes > 0 else 0
        }
        for (first_name, last_name, name, picture_url), votes in resultat.items()
    ]
    return resultat_pourcentage

def decompte_votes_par_pays(election, Vote, Candidate):
    pays_participants = Vote.objects.filter(election=election, is_valid=True, is_counted=True) \
        .values_list('country', flat=True).distinct()
    resultat_par_pays = {}

    for pays in pays_participants:
        votes_par_pays = Vote.objects.filter(election=election, country=pays, is_valid=True, is_counted=True) \
            .values('candidate_token') \
            .annotate(count_votes=Count('id')) \
            .order_by('-count_votes')
        resultat_par_pays[pays] = []
        total_votes_pays = Vote.objects.filter(election=election, country=pays, is_valid=True, is_counted=True).count()
        candidats = Candidate.objects.filter(election=election)
        for candidat in candidats:
            vote_candidat = next((v['count_votes'] for v in votes_par_pays if decrypt_message(v['candidate_token']) == candidat.candidate_token), 0)
            pourcentage_votes = (vote_candidat / total_votes_pays) * 100 if total_votes_pays > 0 else 0
            resultat_par_pays[pays].append({
                'first_name': candidat.first_name,
                'last_name': candidat.last_name,
                'name': candidat.name,
                'picture_url': candidat.picture.url,
                'votes': vote_candidat,
                'percentage': pourcentage_votes
            })
    return resultat_par_pays
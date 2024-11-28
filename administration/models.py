from django.db import models
from django.utils import timezone
import uuid
from eVoting_Ceni.utils import hash_message, encrypt_message, decrypt_message
from elector.models import *

class Election(models.Model):
    election_code = models.CharField(max_length=50, unique=True)
    election_name = models.CharField(max_length=50)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    status = models.CharField(max_length=50, default="created")
    electors = models.ManyToManyField(Elector, related_name="elections", blank=True)

    class Meta:
        verbose_name = 'Election'
        verbose_name_plural = 'Elections'
    
    @property
    def electors_count(self):
        return self.electors.count()
    
    @property
    def candidates_count(self):
        return self.candidates.count()
    
    def __str__(self):
        return self.election_code

class Candidate(models.Model):
    national_number = models.CharField(max_length=100, unique=True)
    candidate_token = models.CharField(max_length=100, unique=True)
    election = models.ForeignKey(Election, related_name='candidates', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to='profile_pics')
    party = models.CharField(max_length=50)
    
    class Meta:
        verbose_name = 'Candidate'
        verbose_name_plural = 'Candidates'

    def save(self, *args, **kwargs):
        if not self.pk:
            self.national_number = hash_message(self.national_number)
            self.candidate_token = hash_message(str(uuid.uuid4()))
        super(Candidate, self).save(*args, **kwargs)

    def __str__(self):
        return self.national_number

class Vote(models.Model):
    vote_code = models.CharField(max_length=100, unique=True)
    elector_token = models.BinaryField()
    candidate_token = models.BinaryField(blank=True, null=True)
    election = models.ForeignKey(Election, related_name="votes", on_delete=models.CASCADE)
    country = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_blank = models.BooleanField(default=False)
    is_valid = models.BooleanField(default=False)
    is_counted = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = 'Votes'
        
    def save(self, *args, **kwargs):
        if not self.pk: 
            self.vote_code = hash_message(str(uuid.uuid4()))
            self.elector_token = encrypt_message(self.elector_token)
    
            if not self.is_blank:
                if self.candidate_token:
                    self.candidate_token = encrypt_message(self.candidate_token)
                else:
                    self.candidate_token = None
        super(Vote, self).save(*args, **kwargs)
        
    @property
    def elector_token_decrypt(self):
        return decrypt_message(self.elector_token) if self.elector_token else None
    
    @property
    def candidate_token_decrypt(self):
        return decrypt_message(self.candidate_token) if self.candidate_token else None

    def __str__(self):
        return self.vote_code

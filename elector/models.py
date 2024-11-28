from django.db import models
from users.models import User
from eVoting_Ceni.utils import hash_message
import uuid

class ElectoralList(models.Model):
    national_number = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    country = models.CharField(max_length=100)
    election = models.ForeignKey('administration.Election', related_name='electorlists', on_delete=models.CASCADE)
    
    class Meta:
        verbose_name = "ElectoralList"
        verbose_name_plural = "ElectoralLists"
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.national_number = hash_message(self.national_number)
        super(ElectoralList, self).save(*args, **kwargs)

    def __str__(self):
        return self.national_number

class Elector(User):
    national_number = models.CharField(max_length=100, unique=True)
    elector_token = models.CharField(max_length=100, unique=True)
    country =   country = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Elector"
        verbose_name_plural = "Electors"
        
    def save(self, *args, **kwargs):
        if not self.pk:
            self.elector_token =  hash_message(str(uuid.uuid4()))
        super(Elector, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.national_number
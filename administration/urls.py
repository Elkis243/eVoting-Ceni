from django.urls import path
from .views import *

urlpatterns = [
    path('election', ElectionView.as_view(), name='election'),
    path('edit_election/<int:pk>', EditElection.as_view(), name='edit_election'),
    path('import_list/<int:pk>', import_list, name='import_list'),
    path('extend_election/<int:pk>', ExtendElection.as_view(), name='extend_election'),
    path('active_election/<int:pk>', activeVoting, name='active_election'),
    path('cancel_election/<int:pk>', cancelVoting, name='cancel_election'),
    path('close_election/<int:pk>', closeVoting, name='close_election'),
    path('published_voting/<int:pk>', publishedVoting, name='published_voting'),
    path('candidate/<int:pk>', CandidateView.as_view(), name='candidate'),
    path('consult_election/<int:pk>', detail_election, name='consult_election'),
    path('delete_candidate/<int:pk>', deleteCandidate, name="delete_candidate"),
]
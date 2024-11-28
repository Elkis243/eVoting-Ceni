from django.urls import path
from .views import *

urlpatterns = [
    path('list_candidate', ListCandidate.as_view(), name="list_candidate"),
    path('choice_candidate/<int:pk>', ChoiceCandidate.as_view(), name="choice_candidate"),
    path("choice_white_vote", ChoiceWhiteVote.as_view(), name="choice_white_vote"),
    path('history', history, name='history'),
    path('view_result/<int:pk>', view_result, name='view_result'),
    path('verify', verify, name='verify')
]

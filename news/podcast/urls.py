from django.urls import path
from .views import search_feeds, get_articles, transcribe_to_audio

urlpatterns = [
    path('search_feeds', search_feeds),
    path('get_articles', get_articles),
    path('transcribe_to_audio', transcribe_to_audio),
]

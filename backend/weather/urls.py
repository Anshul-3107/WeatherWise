from django.urls import path
from . import views

urlpatterns = [
    path('current/', views.get_current_weather, name='current-weather'),
    path('search/', views.search_city, name='search-city'),
    path('air-quality/', views.get_air_quality, name='air-quality'),
    path('predict/', views.get_prediction, name='weather-prediction'),
    path('advice/', views.get_advice, name='personalized-advice'),
]
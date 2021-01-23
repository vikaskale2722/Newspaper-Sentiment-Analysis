from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('readNews', views.readNewsPage, name="read_news"),
    path('sentimentNews/', views.sentimentNewsPage, name="sentiment_news"),
    path('overallsentimentNews/', views.overallSentimentNewsPage, name="overall_news"),
]
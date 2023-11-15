from django.urls import path
from . import views

urlpatterns = [
    path('', views.my_view, name='my-template'),
    path('traffic/', views.traffic, name='traffic'),
]

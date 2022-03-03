from django.urls import path

from . import views

app_name = 'usuarioapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('equacoes', views.equacoes, name='equacoes'),
]

from django.urls import path

from . import views

app_name = 'equipamentos'

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:equipamento_id>', views.equipamento, name='equipamento'),
]

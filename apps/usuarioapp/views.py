from django.shortcuts import render
from django.http import JsonResponse
from django.urls import reverse


# Listagem do Equipamento
def index(request):

    return render(request, 'index.html')


def home(request):
    ''' da pagina principal. Temporariamente usando para testes '''
    return render(request, 'index.html')


def equacoes(request):
    return render(request, 'equacoes/index.html')

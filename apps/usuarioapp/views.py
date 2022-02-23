from django.shortcuts import render
from django.http import JsonResponse
from apps.capitalcost.project import teste_print
from turtonapp.services import temporarySeeder
from django.urls import reverse


# Listagem do Equipamento
def index(request):

    return render(request, 'index.html')


def home(request):
    ''' da pagina principal. Temporariamente usando para testes '''
    return render(request, 'index.html')


def equacoes(request):
    return render(request, 'equacoes/index.html')


def seedCreator(request):
    data = temporarySeeder()
    return render(request, 'testes/seeder.html', data)

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse


# Listagem do Equipamento
def index(request):

    return render(request, 'equipamentos/index.html', dados)


# Detalhes do Equipamento
def equipamento(request, equipamento_id):

    return render(request, 'equipamento.html', dados)

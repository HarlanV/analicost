from django.shortcuts import render
from django.http import JsonResponse
from .models import HistoricoFluxoCaixa
from django.views.generic import View
from turtonapp import services


class HomeView(View):

    def index(request):
        tabela = HistoricoFluxoCaixa.objects.values('descricao', 'valor')
        data = list(tabela)
        export_data = {
            "dados": data
        }
        # return JsonResponse(data, safe=False)
        return render(request, 'custos/index.html', export_data)

    def get_data(request, *args, **kwargs):
        tabela = HistoricoFluxoCaixa.objects.values('descricao', 'valor')
        data = list(tabela)
        return JsonResponse(data, safe=False)

    def report(request):
        num = 100
        report = services.getProjectReport(num)

        dados = {
            'project': report["project"],
            'equipments': report["equipments"],
            'equipmentsDetails': report["equipmentsDetails"]
        }

        teste_print(dados)

        return render(request, 'custos/relatorios/capex.html', dados)


def teste_print(dados):
    print('--------------------------------------')
    print('--------------------------------------')
    print(dados)
    print('--------------------------------------')
    print('--------------------------------------')

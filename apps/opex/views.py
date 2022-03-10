from django.shortcuts import redirect, render
from capex.equipments.equipments import teste_print
from capex import services
from django.views.generic import View
from opex import services
from capex import services as capexServices


# Referente à tela de Constantes Operacionais e suas opções
class ConstantsConfig(View):

    def index(request):

        list_projects = capexServices.ProjectServices.listProjects()

        if not list_projects:
            dados = {}
            return render(request, 'custos/opex_config/auxiliar_factors.html', dados)

        num = list_projects[0]
        return redirect('opex:opex_config', project=num)

    # Formulário de edição das Operational Constants
    def formConstants(request, project):
        # lista todos os projetos atualmente
        list_projects = capexServices.ProjectServices.listProjects()

        # service auxiliar
        service = services.OpexServices(project)

        # Fatores auxiliar no calculo de equações
        auxiliateFactors = service.getAuxiliateFactors(project)
        equation = service.createComEquation(auxiliateFactors)
        projectCapex = service.project
        opex = service.getOpex(project)
        project_settings = service.getProjectSettings(project)
        utilities_constants = service.getUtilitiesConstants(project)

        dados = {
            'list_projects': list_projects,
            'project': project,
            'auxiliate_factors': auxiliateFactors,
            'equation': equation,
            'fcil_source': service.listForms()["fcilSource"],
            'projectCapex': projectCapex,
            'cut_constants': service.listForms()["cut_constants"],
            'opex': opex,
            'project_settings': project_settings,
            'utilites_constants': utilities_constants
        }

        return render(request, 'custos/opex_config/auxiliar_factors.html', dados)

    def configPOST(request, project):
        data = {
            'args': dict(request.POST.items()),
            'project': project
        }

        service = services.OpexServices(project)

        service.updateOpexConfig(**data)
        # getattr(services.OpexServices(project), 'updateOpexConfig')(**data)

        return redirect('opex:opex_config', project=project)


# Referente à tela de materiais e suas opções
class Material(View):
    def index(request):

        list_projects = capexServices.ProjectServices.listProjects()

        if not list_projects:
            dados = {}
            return render(request, 'custos/opex_config/auxiliar_factors.html', dados)

        num = list_projects[0]
        return redirect('opex:opex_material', project=num)
        pass

    def listMaterials(request, project):
        # lista todos os projetos atualmente
        list_projects = capexServices.ProjectServices.listProjects()

        # service auxiliar
        data = {
            'list_projects': list_projects,
            'project': project,
            'material': services.OpexServices(project).getAllMaterials()
        }

        service = services.OpexServices(project)
        return render(request, 'custos/material/material.html', data)

    def createForm(request, project):
        fields = services.OpexServices().formCreateMaterial()
        data = {
            'options': fields['options'],
            'buying_price_unity': fields['buying_price_unity'],
            'material_flow_unity': fields['material_flow_unity'],
            'project': project
        }

        return render(request, 'custos/material/formMaterial.html', data)

    def createFormPost(request, project):
        args = dict(request.POST.items())
        args.pop('csrfmiddlewaretoken', None)
        service = services.OpexServices(project).formInsertMaterial(args)
        return redirect('opex:opex_material', project=project)

    def removeMaterial(request, project, material):
        service = services.OpexServices(project)
        service.removeMaterial(material)
        return redirect('opex:opex_material', project=project)


class Utilities(View):

    # Renderiza formulário de configuração das utilities do equipamento
    def configEquipment_GET(request, project, equipamento_id):
        equipment = capexServices.EquipmentServices.getEquipmentInProject(equipamento_id)
        if equipment.equipment.utility_form is None:
            return redirect('capex:project', project=project)
        options = services.OpexServices(project).getUtilitieEquipmentOptions(project, equipment)
        path = "equipamentos/utilities_form/"
        form = str(equipment.equipment.utility_form).lower()
        path = path + form + ".html"
        options["project"] = project
        options["equipment_project_id"] = equipamento_id
        options["equipment_project"] = equipment
        options["equipment"] = equipment.equipment
        # return redirect('capex:project', project=project)
        return render(request, path, options)

    # Salva as informações de Utilities do equipamento
    def configEquipment_POST(request, project, equipamento_id):
        args = dict(request.POST.items())
        args.pop('csrfmiddlewaretoken', None)
        equipment = capexServices.EquipmentServices.getEquipmentInProject(equipamento_id)
        services.OpexServices(project).postUtilitesConfig(equipment, args)
        return redirect('capex:project', project=project)


class CashFlow(View):

    def index(request):
        list_projects = capexServices.ProjectServices.listProjects()
        if request.method == 'POST':
            project = int(request.POST["project"])
            method = request.POST["depreciationMethod"]
            dTime = int(request.POST["depreciationTime"])
            data = CashFlow.cashFlowGenerate(project, method, dTime)
            teste_print(data)
            return render(request, 'custos/cash_flow/index.html', data)

        else:
            data = {
                'list_projects': list_projects,
                'dkOptions': ["MACRS", "Straight"]
            }
            return render(request, 'custos/cash_flow/configCashFlow.html', data)

    # Pode ser remanejado para services.
    def cashFlowGenerate(project, depreciationMethod, depreciationTime):
        data = services.CashFlowService(project).getCashFlowData(depreciationMethod, depreciationTime)

        values = data.copy()
        values = zip(
            values['years'],
            values['investiment'],
            values['dk'],
            values['revenue'],
            values['comd'],
            values['netprofit'],
            values['CashFlowNonDisconted'],
            values['CashFlowDisconted'],
            values['CumulativeNonDiscontedCF'],
            values['CumulativeDiscontedCF']
        )
        data = {
            'values': values,
            'render': True,
            'chartYValues': data['CumulativeDiscontedCF'],
            'chartXValues': data['years'],

        }

        return data

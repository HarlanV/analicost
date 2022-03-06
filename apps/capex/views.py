from django.http import JsonResponse
from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from capex import services
from capex.equipments.equipments import teste_print


# Busca todos os projetos e REDIRECIONA para a pagina do primerio projeto na lista, caso tenha algum
def index(request):

    list_projects = services.ProjectServices.listProjects()

    if not list_projects:
        dados = {}
        return render(request, 'project/index.html', dados)

    num = list_projects[0]
    return redirect('capex:project', project=num)


# Renderiza pagina de criação do projeto
def createProject(request):
    if request.method == "POST":
        num = int(request.POST["projectNum"])
        cepci = float(request.POST["cepci"])
        project = services.ProjectServices
        project = project.createProject(num, cepci)
        return redirect('capex:project', project=num)

    else:
        return render(request, 'project/create-project.html')


# Retorna a pagina e relatorio e equipamentos do projeto
def projectReport_GET(request, project):
    list_projects = services.ProjectServices.listProjects()
    list_equipments = services.EquipmentServices.allEquipments()
    report = services.ProjectServices.getProjectReport(project)
    dados = {
        'list_projects': list_projects,
        'list_equipments': list_equipments,
        'tables_list': report["list_equipmments"],
        'project': report["project"],
        'equipments': report["equipments"],
        'equipmentsDetails': report["equipmentsDetails"],
    }

    return render(request, 'project/index.html', dados)


# Renderiza o FORMULÁRIO de inserção de um equipamento NO PROJETO
def addEquipmentProjectForm_GET(request, project, equipamento_id):

    options = services.EquipmentServices.equiptmentFormOptions(equipamento_id)
    options["project"] = project
    equipmentUrl = options["equipment"].name.lower().replace(" ", "_")
    url = "equipamentos/equipment-form/" + equipmentUrl + ".html"
    return render(request, url, options)


# Inserção de equipamentos no projeto
def addEquipmentProject_POST(request, project, equipamento_id):

    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.POST.items())
    }

    getattr(services.EquipmentServices, 'addEquipmentToProjec')(**data)
    return JsonResponse(status=201, data={'status': 'false', 'message': "Adicionado com sucesso"})
    # return redirect('capex:project', project=project)


# Armazena dados do equipamento no projeto
def updateEquipment_POST(request, project, equipamento_id):
    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.POST.items())
    }

    getattr(services.EquipmentServices, 'updateEquipmentInProjec')(**data)
    return redirect('capex:project', project=project)


def equipmentCost(request, project, equipamento_id):
    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.GET.items())
    }
    costs = getattr(services.EquipmentServices, 'getEquipmentPrice')(**data)

    return JsonResponse(costs)


# TODO: fazer retrocesso para remover unity das rotas chamadas.
# Função sendo desativada
def attributeRange(request, equipamento_id, unity):

    data = {
        'equipment_id': equipamento_id,
        'args': dict(request.GET.items())
    }

    range = getattr(services.EquipmentServices, 'getRangeAttributes')(**data)

    return JsonResponse(range)


# Remove o equipamento do projeto
def removeEquipment_DELETE(request, project, equipamento_id):
    sucesso = services.ProjectServices().removeEquipment(project, equipamento_id)
    data = {
        'sucesso': sucesso
    }
    return JsonResponse(data)


# Remove o projeto atual completamente
def deleteProject_DELETE(request, project):
    sucesso = services.ProjectServices().deleteProject(project)
    data = {
        'sucesso': sucesso
    }
    return JsonResponse(data)


# Renderiza formuláio de atualização do equipamento
def updateEquipment_GET(request, project, equipamento_id):
    equipment = services.EquipmentServices.getEquipmentInProject(equipamento_id)
    options = services.EquipmentServices.equiptmentFormOptions(equipment.equipment.id)
    options["project"] = project
    options["equipment_project_id"] = equipamento_id
    equipmentUrl = options["equipment"].name.lower().replace(" ", "_")

    # informação de equipamento..
    options['equipment_data'] = equipment
    #
    url = "equipamentos/edit_form/" + equipmentUrl + ".html"
    return render(request, url, options)


# Renderiza formulário de configuração das utilities do equipamento
def configEquipment_GET(request, project, equipamento_id):
    equipment = services.EquipmentServices.getEquipmentInProject(equipamento_id)
    if equipment.equipment.utility_form is None:
        return redirect('capex:project', project=project)

    options = services.EquipmentServices.getUtilitieEquipmentOptions(project, equipment)
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
    equipment = services.EquipmentServices.getEquipmentInProject(equipamento_id)
    # Is efficiency
    if len(args) == 1:
        services.EquipmentServices.updateUtilitieEquipmentOptions(equipment, args)
    else:
        services.EquipmentServices().prepareUtilitiesValues(equipment, args)
    return redirect('capex:project', project=project)

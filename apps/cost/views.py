from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from django.http import HttpResponse
from turtonapp import services


# Listagem do Equipamento
def index(request):
    list_projects = services.ProjectServices.listProjects()

    if not list_projects:
        dados = {}
        return render(request, 'project/index.html', dados)

    num = list_projects[0]
    return redirect('turton:project', project=num)


def createProject(request):
    if request.method == "POST":
        num = int(request.POST["projectNum"])
        cepci = float(request.POST["cepci"])
        project = services.ProjectServices
        project = project.createProject(num, cepci)
        return redirect('turton:project', project=num)

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


# POST para insert de Equipamento no Projeto
def addEquipmentProject_POST(request, project, equipamento_id):
    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.POST.items())
    }

    getattr(services.EquipmentServices, 'addEquipmentToProjec')(**data)
    return redirect('turton:project', project=project)


# POST para insert de Equipamento no Projeto
def updateEquipment_POST(request, project, equipamento_id):
    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.POST.items())
    }

    getattr(services.EquipmentServices, 'updateEquipmentInProjec')(**data)
    return redirect('turton:project', project=project)


def equipmentCost(request, project, equipamento_id):

    data = {
        'equipment_id': equipamento_id,
        'project': project,
        'args': dict(request.GET.items())
    }

    costs = getattr(services.EquipmentServices, 'getEquipmentPrice')(**data)

    return JsonResponse(costs)


def attributeRange(request, equipamento_id, unity):

    type = request.GET["type"]
    specification = float(request.GET["equipment_attribute"])

    args = {
        'equipment_id': equipamento_id,
        'specification': specification,
        'type': type,
        'id_unity': unity
    }
    range = getattr(services.EquipmentServices, 'getRangeAttributes')(**args)

    return JsonResponse(range)


def removeEquipment_DELETE(request, project, equipamento_id):
    sucesso = services.ProjectServices().removeEquipment(project, equipamento_id)
    data = {
        'sucesso': sucesso
    }
    return JsonResponse(data)


def deleteProject_DELETE(request, project):
    sucesso = services.ProjectServices().deleteProject(project)
    data = {
        'sucesso': sucesso
    }
    return JsonResponse(data)


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
    pass


def updateEquipment_PUT(request, project, equipamento_id):
    pass


def teste_print(dados):
    print('--------------------------------------')
    print('--------------------------------------')
    print(dados)
    print('--------------------------------------')
    print('--------------------------------------')

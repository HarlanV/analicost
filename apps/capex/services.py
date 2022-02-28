from django.db.models import Q
from django.shortcuts import get_object_or_404
from capex.equipments.project import ProjectCost
from .models import BareModule, ComplementConstants, Equipment, MaterialFactor, PressureFactor, PurchasedFactor, EquipmentUnity, Dimension
from capex.models import CapexProject, Cepci, EquipmentProject


class EquipmentServices():

    # Listagem do Equipamento
    def allEquipments():
        equipamento = Equipment.objects.all()
        return equipamento

    def getEquipmentFromId(id):
        return Equipment.objects.get(id=id)

    def getEquipmentInProject(id):
        equipment = get_object_or_404(EquipmentProject, pk=id)
        return equipment

    def getEquipmentPrice(equipment_id, project, args):
        project = ProjectCost(project, True)
        args['cepci'] = project.project.cepci
        args['equipment_id'] = int(equipment_id)

        equipment = findEquipmentPath(
            EquipmentServices.getEquipmentFromId(equipment_id),
            'EquipmentCosts', {
                'args': args,
                'equipment_id': equipment_id
            }
        )
        costs = {
            'bareCost': equipment.purchasedEquipmentCost,
            'bareModule': equipment.bareModuleCost
        }

        return costs

    def equiptmentFormOptions(id):
        form = infoReport(id)
        form = form.makeform()
        return form

    def addEquipmentToProjec(equipment_id: int, project: int, args: dict):
        """
        kwargs: (equipment_id, project, args)
        """

        project = ProjectCost(project, True)
        args['cepci'] = project.project.cepci
        args['equipment_id'] = int(equipment_id)

        equipment = findEquipmentPath(
            EquipmentServices.getEquipmentFromId(equipment_id),
            'EquipmentCosts',
            {
                'equipment_id': equipment_id,
                'args': args
            }
        )

        # equipment = EquipmentCosts(equipment_id, args, False) #fobCost
        equipment.insertIntoProject(project)

        return True

    def updateEquipmentInProjec(equipment_id: int, project: int, args: dict):
        """
        kwargs: (equipment_id, project, args)
        """
        equipmentProject = EquipmentServices.getEquipmentInProject(equipment_id)
        project = ProjectCost(project, True)
        args['cepci'] = project.project.cepci
        # TODO: Verificar se é necessário esse id. no insert tbm!
        args['equipment_id'] = int(equipmentProject.equipment.id)

        equipmentCost = findEquipmentPath(
            EquipmentServices.getEquipmentFromId(equipmentProject.equipment.id),
            'EquipmentCosts', {
                'equipment_id': equipmentProject.equipment.id,
                'args': args
            }
        )

        equipmentCost.updateInProject(project, equipmentProject)

        return True

    def getProjectReport(n):
        projectCost = ProjectCost(n)
        equipments = projectCost.equipments
        equipmentsDetails = list(map(lambda x: [x.equipment, x.equipment.dimension], equipments))
        info = {
            'project': projectCost.project,
            'equipments': list(projectCost.equipments),
            'equipmentsDetails': equipmentsDetails,
            'dimension_unity': ''
        }

        return info

    def getRangeAttributes(equipment_id, args):

        equipmentForm = EquipmentServices.getEquipmentFromId(equipment_id)

        # equipment = FobCost(equipment_id, args)
        equipment = findEquipmentPath(equipmentForm, 'FobCost', {
            'equipment_id': equipment_id,
            'args': args
        })

        # equipment = FobCost(equipment_id, args)
        unitysConstants = EquipmentUnity.objects.filter(Q(dimension=equipment.equipment.dimension, is_default=True) | Q(id=args["attribute_dimension"]))
        conversor = 1

        # (TODO: ver se não seria melhor colocar esse trecho dentro da classe de equipamentos)
        if unitysConstants.count() > 1:
            if unitysConstants.first().is_default is True:
                conversor = (unitysConstants[1].convert_factor) / (unitysConstants[0].convert_factor)
            else:
                conversor = (unitysConstants[0].convert_factor) / (unitysConstants[1].convert_factor)
        else:
            pass  # (TODO: Exception aqui depois)

        range = {
            'max': equipment.maxAttribute * conversor,
            'min': equipment.minAttribute * conversor
        }
        return range


class infoReport():

    def __init__(self, id):
        self.id = id
        self.q = PurchasedFactor.objects.filter(equipment_id=id)
        self.equipment = self.q.first().equipment

    # Define qual o formulario a ser chamado e retorna o valor
    def makeform(self):
        args = {
            'q': self.q,
            'equipment': self.equipment
        }
        instancia = findEquipmentPath(self.equipment, 'EquipmentComplementData', args)

        self.equipmentForm = instancia.form()
        self.equipmentForm["equipment_id"] = self.id

        return self.equipmentForm


class ProjectServices():

    def listProjects():
        projects = CapexProject.objects.all()
        projectsNums = list(map(lambda x: x.project_number, projects))
        return projectsNums

    def getProjectReport(n):
        projectCost = ProjectCost(n)
        equipments = projectCost.equipments
        equipmentsDetails = list(map(lambda x: [x.equipment, x.equipment.dimension], equipments))
        info = {
            'project': projectCost.project,
            'equipments': list(projectCost.equipments),
            'list_equipmments': projectCost.listDistinctEquipment,
            'equipmentsDetails': equipmentsDetails,
            'dimension_unity': ''
        }

        return info

    def createProject(number, cepci):
        project = CapexProject(project_number=number, cepci=cepci)
        project.save()

    def removeEquipment(self, project, equipment_id):
        deleted = ProjectCost(project).removeEquipment(equipment_id)
        return deleted

    def deleteProject(self, project):
        deleted = ProjectCost(project).removeProject()
        return deleted


def findEquipmentPath(equipment, equipmentClass, args=None, genericEquipment=None):
    """
    equipment:Equipment, equipmentClass:string, args=None
    """
    name = equipment.name.lower().replace("-", "_").replace(" ", "_")
    equipmentPath = "capex.equipments." + name
    mod = __import__(equipmentPath, fromlist=[equipmentClass])

    if args is not None:
        response = getattr(mod, equipmentClass)(**args)
    else:
        response = getattr(mod, equipmentClass)()
    return response

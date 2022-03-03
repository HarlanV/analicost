from django.db.models import Q
from django.shortcuts import get_object_or_404
from capex.equipments.equipments import teste_print
from opex.models import EquipmentsUtilitiesSetting, ProjectUtilitiesConstant
from capex.equipments.project import ProjectCost
from .models import Equipment, PurchasedFactor, EquipmentUnity
from capex.models import CapexProject, EquipmentProject


# TODO: criar padrão de projeto para funções.
# Services para comunicação com models e classes referente aos equipamentos do CAPEX
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
        project = ProjectCost(project)
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

        project = ProjectCost(project)
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
        project = ProjectCost(project)
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

    def getUtilitieEquipmentOptions(project, equipment):
        constants = ProjectUtilitiesConstant.objects.filter(project__project_number=project)
        values = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id).first()
        utility = None
        if values is not None:
            utility = values.utility
            
        form = str(equipment.equipment.utility_form)
        form = form.lower()
        if form == "efficiency":
            dataForm = {
                'efficiency': values.efficiency
            }
        if form == "thermal":
            dataForm = {
                'Steam': constants.filter(classification="Steam from Boilers").all(),
                'ThermalSystems': constants.filter(classification="Thermal Systems").all(),
                'Water': constants.filter(classification="Water").all(),
                'Refrigeration': constants.filter(classification="Refrigeration").all(),
                'UtilitiesTypes': ['Heating Utilities', 'Cooling Utilities', 'User Defined'],
                'formsList': ['Steam', 'ThermalSystems', 'Water', 'Refrigeration'],
                'values': utility,
                'cost_unitys': EquipmentUnity.objects.filter(dimension__dimension="Energy Cost"),
                'duty_unitys': EquipmentUnity.objects.filter(dimension__dimension="Power"),
            }
        # TODO: Opção para remoção futura do steam de Drives nas configurações.
        if form == "steam":
            dataForm = {
            }

        if form == "energy":
            dataForm = {
                'Steam': constants.filter(classification="Steam from Boilers").all(),
                'ThermalSystems': constants.filter(classification="Thermal Systems").all(),
                'Eletricity': constants.filter(aka="Eletricity").all(),
                'Values': utility
            }
        return dataForm

    def updateUtilitieEquipmentOptions(equipment, args):
        utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)
        utilities.update(**args)

    def prepareUtilitiesValues(self, equipment, args):
        utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)
        args["duty_unity"] = EquipmentUnity.objects.get(id=args["duty_unity"])

        if args["utype"] != "User Defined":
            args["utility"] = ProjectUtilitiesConstant.objects.get(id=args["utility"])
            cost = self.calculateCost(float(args["duty"]), args["utility"].value, args["duty_unity"])
            
        else:
            cost = self.calculateCost(float(args["duty"]), args["utility_cost"], args["duty_unity"])
            args["annual_cost"] = cost
            args.pop('utility_cost', None)

        # em comum
        args.pop('utype', None)
        args["duty"] = args["duty"]
        args["cost_unity"] = EquipmentUnity.objects.filter(unity="GJ").first()
        args["equipment"] = equipment
        teste_print(args)
        if not utilities:
            teste_print("entrou 01")
            equipment = EquipmentsUtilitiesSetting(**args)
            equipment.save()
        else:
            teste_print("entrou 02")
            utilities.update(**args)

    def convertEnergyUnity(self, unity: EquipmentUnity, reference: str, value: float):
        defaultPressureFactor = EquipmentUnity.objects.filter(unity=reference).first()
        return ((defaultPressureFactor.convert_factor) / (unity.convert_factor))

        pass

    def calculateCost(self, duty: float, utility_cost: float, duty_unity: EquipmentUnity):
        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        valueInGJ = self.convertEnergyUnity(duty_unity, "GJ", duty)
        return (float(valueInGJ) * float(utility_cost) * (timeWorked.value))


# Auxilia na busca de informações necessárias na montagem de formulário dos equipamentos
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


# TODO: criar padrão de projeto para funções.
# Services para comunicação com models e classes referente aos projetos
class ProjectServices():

    def getProjectFromNum(projectNumber):
        return CapexProject.objects.filter(project_number=projectNumber).first()

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
        # TODO: Puxar CEPCI por ano caso não seja inserido. Nova feature
        p = ProjectCost(number)
        project = p.createProject(number, cepci)

    def removeEquipment(self, project, equipment_id):
        deleted = ProjectCost(project).removeEquipment(equipment_id)
        return deleted

    def deleteProject(self, project):
        deleted = ProjectCost(project).removeProject()
        return deleted

    def updateFieldProject(project: CapexProject, field: str, value):
        setattr(project, field, value)
        project.save()
        return project

    def updateProject(project: CapexProject, data: dict):
        project.update(**data)


# Função auxiliar para chamar dinamicamente os modulos de equipamentos 
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

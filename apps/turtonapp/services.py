from django.db.models import Q

from django.shortcuts import get_object_or_404
from .models import BareModule, ComplementConstants, Equipment, MaterialFactor, PressureFactor, PurchasedFactor
from capitalcost.models import CapexProject, Cepci
from turtonapp import capex
from turtonapp.models import Dimension
from equipamentos.models import EquipmentUnity


class EquipmentServices():

    # Listagem do Equipamento
    def allEquipments():
        equipamento = Equipment.objects.all()
        return equipamento

    def get_equipment(id, type=None, specification=None):
        if type is None:
            equipment = get_object_or_404(Equipment, pk=id)

        # equipment = get_object_or_404(Equipment, pk=id)
        # equipamentos = get_object_or_404(PurchasedFactor, pk=id)
        return equipment

    def getEquipmentPrice(equipment_id, project, args):
        """
        [EM MANUTENÇÃO]
        """
        project = capex.ProjectCost(project, True)
        args['cepci'] = project.project.cepci
        args['equipment_id'] = int(equipment_id)
        equipment = capex.EquipmentCost(equipment_id, args, True)

        costs = {
            'bareCost': equipment.purchasedEquipmentCost,
            'bareModule': equipment.bareModuleCost
        }

        return costs

    def equiptmentFormOptions(id):
        form = EquipmentFormConfig(id)
        form = form.makeform()
        return form

    def addEquipmentToProjec(equipment_id: int, project: int, args: dict):
        """
        kwargs: (equipment_id, project, args)
        """

        project = capex.ProjectCost(project, True)
        args['cepci'] = project.project.cepci
        args['equipment_id'] = int(equipment_id)

        equipment = capex.EquipmentCost(equipment_id, args, True)
        equipment.insertIntoProject(project)

        return True

    def getProjectReport(n):
        projectCost = capex.ProjectCost(n)
        equipments = projectCost.equipments
        equipmentsDetails = list(map(lambda x: [x.equipment, x.equipment.dimension], equipments))
        info = {
            'project': projectCost.project,
            'equipments': list(projectCost.equipments),
            'equipmentsDetails': equipmentsDetails,
            'dimension_unity': ''
        }

        return info

    def getRangeAttributes(equipment_id, specification, type, id_unity):
        args = {
            'equipment_id': int(equipment_id),
            'type': type,
            'specification': float(specification),
        }

        equipment = capex.EquipmentCost(equipment_id, args, False, True)
        
        unitysConstants = EquipmentUnity.objects.filter(Q(dimension=equipment.equipment.dimension, is_default=True) | Q(id=id_unity))
        
        conversor = 1
        if unitysConstants.count() > 1:
            if unitysConstants.first().is_default is True:
                # conversor = (unitysConstants[0].convert_factor) / (unitysConstants[1].convert_factor)
                conversor = (unitysConstants[1].convert_factor) / (unitysConstants[0].convert_factor)
            else:
                # conversor = (unitysConstants[1].convert_factor) / (unitysConstants[0].convert_factor)
                conversor = (unitysConstants[0].convert_factor) / (unitysConstants[1].convert_factor)
        else:
            pass  # (TODO: Exception aqui depois)

        range = {
            'max': equipment.maxAttribute * conversor,
            'min': equipment.minAttribute * conversor
        }
        return range


class EquipmentFormConfig():

    def __init__(self, id):
        """
        Esta classe ainda está sob a possibilidade de se tornar um banco de dados.
        Contudo, para fins de desenvolvimento, sesrá feito da maneira menos complexa por enquanto
        kwargs: (equipment_id)
        """

        self.equipmentForm = {}
        self.equipmentForm["equipment_id"] = id

        self.q = PurchasedFactor.objects.filter(equipment_id=id)
        self.equipment = self.q.first().equipment
        self.equipmentForm["equipment"] = self.equipment

    # Defini qual o formulario a ser chamado e retorna o valor
    def makeform(self):
        name = self.equipment.name.lower().replace("-", "_")
        do = f"{name}Form"
        if callable(func := getattr(self, do)):
            func()
        return self.equipmentForm

    def blenderForm(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)

        conversores = {}

        # Verificar se ainda está sendo usado no front. Metodo de calculo foi modificado
        for t in self.equipmentForm["unitys"].values('unity', 'convert_factor', 'is_default'):
            if (t["is_default"]):
                conversores["default"] = t["unity"]
            conversores[t["unity"]] = t["convert_factor"]

        self.equipmentForm["conversores"] = conversores

    def centrifugeForm(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)

    def compressorForm(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)
        self.equipmentForm["materials"] = self.q.values('material').distinct()

    def evaporatorForm(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)
        self.equipmentForm["materials"] = self.q.values('material').distinct()

    def conveyorForm(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)
        self.equipmentForm["materials"] = self.q.values('material').distinct()


class ProjectServices():

    def listProjects():
        projects = CapexProject.objects.all()
        projectsNums = list(map(lambda x: x.project_number, projects))
        return projectsNums

    def getProjectReport(n):
        projectCost = capex.ProjectCost(n)
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
        deleted = capex.ProjectCost(project).removeEquipment(equipment_id)
        return deleted

    def deleteProject(self, project):
        deleted = capex.ProjectCost(project).removeProject()
        return deleted


# Esta função está aqui temporariamente para geração de arquivos json do banco de dados.
def temporarySeeder():
    """
    Dimension
    equipment_unity
    turton_equipment
    turton_purchase_factor
    turton_pressure_factor
    turton_material_factor
    turton_baremodule
    turton_complement_constants
    media_cepci_anual
    """

    data = {}

    # IMPORT DE DIMENSÃO
    dimension = {}
    it = 0
    for d in Dimension.objects.all():
        it += 1
        dim = {
            "dimension": d.dimension,
            "symbol": d.symbol,
            "unity": d.unity,
        }
        dimension[it] = {
            "model": "turtonapp.Dimension",
            "pk": it,
            "fields": dim,
        }

    data["dimension"] = dimension

    # IMPORT DE UNIDADE
    unity = {}
    it = 0
    for d in EquipmentUnity.objects.all():
        it += 1
        dim = {
            "dimension": d.dimension.id,
            "unity": d.unity,
            "unity_math": d.unity_math,
            "convert_factor": d.convert_factor,
            "is_default": d.is_default,
        }
        unity[it] = {
            "model": "equipamentos.EquipmentUnity",
            "pk": it,
            "fields": dim,
        }

    data["EquipmentUnity"] = unity

    # IMPORT DE EQUIPAMENTOS
    equipment = {}
    it = 0
    for d in Equipment.objects.all():
        it += 1
        dim = {
            "name": d.name,
            "description": d.description,
            "dimension": d.dimension.id,
            "symbol": d.symbol,

        }
        equipment[it] = {
            "model": "turtonapp.Equipment",
            "pk": it,
            "fields": dim,
        }

    data["equipment"] = equipment

    # IMPORT DE FATORES DE COMPRA (PurchasedFactor)
    purchase = {}
    it = 0
    for d in PurchasedFactor.objects.all():
        it += 1
        dim = {
            "material": d.material,
            "description": d.description,
            "k1": d.k1,
            "k2": d.k2,
            "k3": d.k3,
            "max_dimension": d.max_dimension,
            "min_dimension": d.min_dimension,
            "fixed_value": d.fixed_value,
            "equipment": d.equipment.id,
            "reference_year": d.reference_year,
            "cepci": d.cepci,

        }
        purchase[it] = {
            "model": "turtonapp.PurchasedFactor",
            "pk": it,
            "fields": dim,
        }

    data["PurchasedFactor"] = purchase

    # IMPORT DE FATORES DE PRESSÃO (PressureFactor)
    pressure = {}
    it = 0
    for d in PressureFactor.objects.all():
        it += 1
        dim = {
            "c1": d.c1,
            "c2": d.c2,
            "c3": d.c3,
            "pressure_min": d.pressure_min,
            "pressure_max": d.pressure_max,
            "condition": d.condition,
            "equipment": d.equipment.id,

        }
        pressure[it] = {
            "model": "turtonapp.PressureFactor",
            "pk": it,
            "fields": dim,
        }

    data["PressureFactor"] = pressure

    # IMPORT DE FATORES DE MATERIAL (MaterialFactor)
    material = {}
    it = 0
    for d in MaterialFactor.objects.all():
        it += 1
        dim = {
            "b1": d.b1,
            "b2": d.b2,
            "fm": d.fm,
            "material": d.material,
            "condition": d.condition,
            "equipment": d.equipment.id,

        }
        material[it] = {
            "model": "turtonapp.MaterialFactor",
            "pk": it,
            "fields": dim,
        }

    data["MaterialFactor"] = material

    # IMPORT DE BareModule (BareModule)
    fbm = {}
    it = 0
    for d in BareModule.objects.all():
        it += 1
        dim = {
            "fbm": d.fbm,
            "calculated": d.calculated,
            "equipment": d.equipment.id,

        }
        fbm[it] = {
            "model": "turtonapp.BareModule",
            "pk": it,
            "fields": dim,
        }

    data["BareModule"] = fbm

    # IMPORT DE ComplementConstants (ComplementConstants)
    complement = {}
    it = 0
    for d in ComplementConstants.objects.all():
        it += 1
        dim = {
            "constant": d.constant,
            "value": d.value,
            "description": d.description,
            "equipment": d.equipment.id,

        }
        complement[it] = {
            "model": "turtonapp.ComplementConstants",
            "pk": it,
            "fields": dim,
        }

    data["ComplementConstants"] = complement

    # IMPORT DE ComplementConstants (ComplementConstants)
    cepci = {}
    it = 0
    for d in Cepci.objects.all():
        it += 1
        dim = {
            "taxa": d.taxa,
            "ano": d.ano,
            "data": d.data,

        }
        cepci[it] = {
            "model": "capitalcost.Cepci",
            "pk": it,
            "fields": dim,
        }

    data["Cepci"] = cepci

    response = {
        'dados': data
    }
    return response


def teste_print(dados):
    print('--------------------------------------')
    print('--------------------------------------')
    print(dados)
    print('--------------------------------------')
    print('--------------------------------------')

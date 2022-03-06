from opex.economic import EconomicConfig, MaterialCost
from capex.models import CapexProject, EquipmentProject


class ProjectCost():
    """
    Attributes: projectNum, project, equipments
    """

    def __init__(self, num=None):
        if num is not None:
            # Checa se projeto já existe...
            hasProject = self.checkProject(num)

            # Importa os dados do projeto para a instancia
            if hasProject is True:
                self.setProject(num)
                self.equipments = self.listEquipmentsProject()
                # self.createProject(num)

    # define o projeto operando no momento. Caso não informado, irá buscar pelo número de projeto
    def setProject(self, num, project=None):
        if project:
            self.projectNum = num
            self.project = project
        else:
            self.projectNum = num
            self.project = self.getProject(num)

    # Retorna um projeto pelo seu numero
    def getProject(self, num):
        project = CapexProject.objects.filter(project_number=num).first()
        return project

    # Retorna qual o projeto sendo trabalho no momento
    def project(self):
        return self.project

    # Persiste um novo projeto
    def createProject(self, num, cepci):
        project = CapexProject(project_number=num, cepci=cepci)
        project.save()
        self.setProject(num, project)
        self.configNewProject()
        return project

    # Adiciona um novo equipamento ao projeto
    def insertEquipment(self, data):
        data['project'] = self.project
        equipment = EquipmentProject(**data)
        equipment.save()
        self.equipments = self.listEquipmentsProject()
        return equipment

    # Atualiza um equipamento no projeto
    def updateEquipment(self, data, equipmentProject):

        data['project'] = self.project
        equipment = EquipmentProject.objects.filter(id=equipmentProject.id)
        equipment.update(**data)
        self.equipments = self.listEquipmentsProject()
        return equipment

    # Atualiza as informações de capex do projeto
    def updateCosts(self):

        project = self.project

        # Zera os contadores de soma
        listEquipments = self.equipments
        purchased_equip_cost = 0
        baremodule_cost = 0
        base_equipment_cost = 0
        base_baremodule_cost = 0

        # Faz as novas somas iterando pelos equipamentos
        for equipment in listEquipments:
            purchased_equip_cost += equipment.purchased_equip_cost
            baremodule_cost += equipment.baremodule_cost
            base_equipment_cost += equipment.base_equipment_cost
            base_baremodule_cost += equipment.base_baremodule_cost

        # project.equipment_code = equipment_code
        project.purchased_equip_cost = purchased_equip_cost
        project.baremodule_cost = baremodule_cost
        project.base_equipment_cost = base_equipment_cost
        project.base_baremodule_cost = base_baremodule_cost

        total_module_cost = self.upRound(baremodule_cost * 1.18)
        project.total_module_cost = total_module_cost
        project.total_grassroot_cost = total_module_cost + self.upRound(0.5 * base_baremodule_cost)
        project.total_equipment_cost = purchased_equip_cost
        project.total_langfactor = project.lang_factor * purchased_equip_cost
        project.save()
        self.project = project
        MaterialCost(self.project).updateAllCosts()

    # Retorna todos os equipamentos atualmente no projeto
    def listEquipmentsProject(self):
        self.equipments = EquipmentProject.objects.filter(project=self.project)
        listDistinctEquipment = (EquipmentProject.objects.filter(project=self.project).values('equipment__name').distinct())
        self.listDistinctEquipment = list(map(lambda x: x["equipment__name"], listDistinctEquipment))
        return self.equipments

    # funcao de arredondamento para valores significativos. Auxiliar.
    def upRound(self, value):
        if (value < 1):
            digits = 3
        else:
            digits = 3 - len(str(round(value)))

        return (round((value / (10**digits))) * (10**digits))

    # Confirma se um projeto já existe
    def checkProject(self, num):
        """
        Confirms if a project already exists, given its number
        """
        project = self.getProject(num)
        # self.setProject(100, project)
        if project:
            return True
        else:
            return False

    # Altera os códigos de equipamentos no projeto
    def renumerar(self, symbol):
        num = self.projectNum
        equipmentLetter = symbol
        initial = equipmentLetter + (str(num)[:1])
        it = 0
        for e in EquipmentProject.objects.filter(equipment_code__contains=initial):
            code = equipmentLetter + str(num + it + 1)
            e.equipment_code = code
            e.save()
            it += 1

        return (equipmentLetter + str(num + it + 1))

    # Remove um equipamento do projeto
    def removeEquipment(self, equipment_id):
        equipment = EquipmentProject.objects.filter(id=equipment_id)
        symbol = equipment.first().equipment.symbol
        delete = equipment.delete()
        self.updateCosts()
        self.renumerar(symbol)

        if delete[0] >= 1:
            return True
        else:
            return False

    # Deleta o projeto completo
    def removeProject(self):
        delete = self.project.delete()

        if delete[0] >= 1:
            return True
        else:
            return False

    # Garante que existe um projeto com a numeração setado, ou retorna um erro.
    def thisRequestAProject(self, num):
        # Checa se projeto já existe...
        hasProject = self.checkProject(num)

        # Caso exista, armazena nos atributos.
        if hasProject is True:
            self.setProject(num)
            self.equipments = self.listEquipmentsProject()
            self.createProject(num)
            return True
        else:
            raise Exception("Project wasn't found.")

    def configNewProject(self):

        config = EconomicConfig(self.project)
        config.setAuxiliarFactorsDefault()
        config.setProjectSettingsDefautl()
        config.setOpexDefault()
        config.setUtilitiesConstantsDefault()

        pass

from capex.models import CapexProject, EquipmentProject


class ProjectCost():
    """
    Attributes: projectNum, project, equipments
    """

    def __init__(self, num, noCreate=False):

        # Checa se projeto já existe...
        hasProject = self.checkProject(num)

        # caso seja solicitado para não criar ou já exista...
        if noCreate is False and hasProject is False:
            self.createProject(num)
        else:
            self.setProject(num)
            self.equipments = self.listEquipmentsProject()

    def setProject(self, num, project=None):
        if project:
            self.projectNum = num
            self.project = project
        else:
            self.projectNum = num
            self.project = self.getProject(num)

    def getProject(self, num):
        project = CapexProject.objects.filter(project_number=num).first()
        return project

    def project(self):
        return self.project

    def createProject(self, num):
        project = CapexProject(project_number=num)
        project.save()
        self.setProject(num, project)
        return project

    def insertEquipment(self, data):
        data['project'] = self.project
        equipment = EquipmentProject(**data)
        equipment.save()
        self.equipments = self.listEquipmentsProject()
        return equipment

    def updateEquipment(self, data, equipmentProject):

        data['project'] = self.project
        equipment = EquipmentProject.objects.filter(id=equipmentProject.id)
        equipment.update(**data)
        self.equipments = self.listEquipmentsProject()
        return equipment

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

    def listEquipmentsProject(self):
        self.equipments = EquipmentProject.objects.filter(project=self.project)
        listDistinctEquipment = (EquipmentProject.objects.filter(project=self.project).values('equipment__name').distinct())
        self.listDistinctEquipment = list(map(lambda x: x["equipment__name"], listDistinctEquipment))
        return self.equipments

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

    def removeProject(self):
        delete = self.project.delete()

        if delete[0] >= 1:
            return True
        else:
            return False


def teste_print(dados):
    print('--------------------------------------')
    print('--------------------------------------')
    print(dados)
    print('--------------------------------------')
    print('--------------------------------------')

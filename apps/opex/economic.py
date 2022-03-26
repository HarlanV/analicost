from capex.equipments.equipments import teste_print
from capex.models import CapexProject, EquipmentProject, EquipmentUnity
from .models import EquipmentsUtilitiesSetting, MaterialCosts, Opex, OpexAuxiliateFactor as AuxiliarFactor, OpexProjectSettings, ProjectUtilitiesConstant, DefaultConstants
from django.db.models import Sum
import numpy_financial as npf


# TODO: Transferir essa classe para services
class MaterialCost():

    def __init__(self, project: CapexProject):
        self.project = project
        # configs = EconomicConfig(project)
        # self.factors = configs.getConfig()
        # capex = self.factor.capex_source

    # Cria um novo material e chama as atualizações necessárias
    def createMaterial(self, args: dict):
        args["annual_cost"] = CostCalculationTools.calculateAnualCost(args["flow"], args["price"], args["flow_unity"], "kg/h")
        material = MaterialCosts(**args)
        material.save()
        self.updateMaterialCosts(args['classification'])
        # return material
        return

    # Remove um material do projeto
    def deleteMaterial(self, idMaterial):
        # consultar material armazenar os campos necessários para atualização posterior
        material = MaterialCosts.objects.get(id=idMaterial)
        classOfMaterial = material.classification
        material.delete()
        self.updateMaterialCosts(classOfMaterial)

        # Atualizar os campos relevantes
        return True

    # Atualiza os valores
    def updateMaterialCosts(self, classification: str):
        """
        for updade all material relational field, classification = "all"
        """
        materials = MaterialCosts.objects.filter(project=self.project)
        opex = Opex.objects.filter(project=self.project).first()
        config = self.checkFieldsUpdate().values()

        if ("Waste" in classification or classification == 'all') and config.first()["cwt_calculated"] is True:
            materialList = materials.filter(classification__contains="Waste")
            cwt = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
            if cwt is None:
                cwt = 0
            opex.cwt = round(cwt, 2)
        if (classification == "Product" or classification == 'all') and config.first()["revenue_calculated"] is True:
            materialList = materials.filter(classification__contains="Product").all()
            revenue = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
            if revenue is None:
                revenue = 0
            opex.revenue = round(revenue, 2)
        if ("Raw" in classification or classification == 'all') and config.first()["crm_calculated"] is True:
            materialList = materials.filter(classification__contains="Raw").all()
            crm = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
            if crm is None:
                crm = 0
            opex.crm = round(crm, 2)
        opex.save()
        self.checkFieldsUpdate()

    # Esta função checa se os campos devem ser atualizados ou estão como input
    def checkFieldsUpdate(self, field="all"):
        configs = OpexProjectSettings.objects.filter(project=self.project)
        if field == "all":
            return configs
        else:
            return configs.values(field)

    # Armazenado para atualização de todos os custos de manufatura do projeto
    def updateAllCosts(self):
        pass
        self.updateMaterialCosts("all")


class UtilityCost():

    def __init__(self, project: CapexProject):
        self.project = project

    def updateUtilitesFromEquipemt(self, equipment, args):

        # significa que é a bomba com a eficiência
        if len(args) == 1:
            utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)

            cost = utilities.first().utility.value
            duty_unity = utilities.first().duty_unity
            equipment_energy = utilities.first().equipment.specification
            utility_cost = utilities.first().utility.value
            args["duty"] = round(equipment_energy / float(args["efficiency"]), 2)
            cost = CostCalculationTools.calculateAnualCost(float(args["duty"]), utility_cost, duty_unity, "GJ")
            args["utility_cost"] = utility_cost
            args["annual_cost"] = round(cost, 2)
            utilities.update(**args)
            return

        utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)
        args["duty_unity"] = EquipmentUnity.objects.get(id=args["duty_unity"])

        if 'utype' in args:
            if args["utype"] == "User Defined":
                args["utility"] = args["utype"]
            args.pop('utype', None)

        if args["utility"] == "User Defined":
            cost = CostCalculationTools.calculateAnualCost(float(args["duty"]), args["utility_cost"], args["duty_unity"], "GJ")
            args["annual_cost"] = round(cost, 2)
            args["utility"] = ProjectUtilitiesConstant.objects.filter(aka="Defined").first()
            args["utility_cost"] = float(args["utility_cost"])
        else:
            args["utility"] = ProjectUtilitiesConstant.objects.get(id=args["utility"])
            cost = CostCalculationTools.calculateAnualCost(float(args["duty"]), args["utility"].value, args["duty_unity"], "GJ",)
            args["annual_cost"] = round(cost, 2)
            args["utility_cost"] = float(args["utility"].value)
            args.pop('utype', None)

        args["duty"] = float(args["duty"])
        args["cost_unity"] = EquipmentUnity.objects.filter(unity="GJ").first()
        args["equipment"] = equipment
        if not utilities:
            equipment = EquipmentsUtilitiesSetting(**args)
            equipment.save()
        else:
            utilities.update(**args)

    def updateCut(self):
        equipments = EquipmentsUtilitiesSetting.objects.filter(equipment__project=self.project).all()
        opex = Opex.objects.filter(project=self.project).first()
        cut = equipments.aggregate(Sum('annual_cost'))["annual_cost__sum"]

        if cut is None:
            cut = 0
        opex.cut = round(cut, 2)
        opex.save()
        pass


class WorkingCapital():
    def __init__(self, project: CapexProject):
        self.project = project

    def updateWorkingCapital(self):
        auxiliar = AuxiliarFactor.objects.filter(project=self.project).first()
        opex = Opex.objects.filter(project=self.project).first()

        auxiliar = AuxiliarFactor.objects.filter(project=self.project).first()
        opex = Opex.objects.filter(project=self.project).first()
        wc = auxiliar.working_capital_a * opex.crm
        wc = wc + (auxiliar.working_capital_b * opex.fcil)
        wc = wc + (auxiliar.working_capital_c * opex.col)
        opex.working_capital = round(wc, 2)
        opex.save()


class OperatingLabor():
    def __init__(self, project: CapexProject):
        self.project = project

    def updateOperatingLabor(self):

        opex = Opex.objects.filter(project=self.project).first()
        equipments = EquipmentProject.objects.filter(project=self.project)
        constants = ProjectUtilitiesConstant.objects.filter(project__project_number=self.project.project_number, aka="Cost of Labor").first()
        Pp = 0
        Nnp = 0
        for e in equipments:
            if e.equipment.isSolid is True:
                Pp = Pp + 1
            elif e.equipment.isSolid is False:
                Nnp = Nnp + 1
        Nol = (6.29 + (31.7 * (Pp**2)) + (0.23 * Nnp))**0.5
        Col = Nol * (1095 / 240) * constants.value
        opex.col = round(Col, 2)
        opex.save()


class ManufactoringCost():
    def __init__(self, project: CapexProject):
        self.project = project

    def updateManufactoringCost(self):
        auxiliar = AuxiliarFactor.objects.filter(project=self.project).first()
        opex = Opex.objects.filter(project=self.project).first()
        auxiliar = AuxiliarFactor.objects.filter(project=self.project).first()
        opex = Opex.objects.filter(project=self.project).first()
        mc = auxiliar.crm * (opex.crm + opex.cwt + opex.cut)
        mc = mc + (auxiliar.col * opex.col)
        mc = mc + (auxiliar.fcil * opex.fcil)
        opex.com = round(mc, 2)
        opex.save()


# Classe a ser chamada sempre que houver atualização dos custos
class EconomicConfig():
    def __init__(self, project: CapexProject):
        self.project = project
        self.setAuxiliarFactor(project)

    # Atualiza as configurações do projeto
    def updateConfig(self, data):
        config = AuxiliarFactor.objects.filter(project=self.project)
        config.update(**data)
        MaterialCost(self.project).updateAllCosts()
        return config

    # Config criada automaticamente na criação do projeto usa valores default
    def setAuxiliarFactorsDefault(self):
        factors = AuxiliarFactor()
        factors.project = self.project
        factors.save()
        return factors

    def setProjectSettingsDefautl(self):
        settings = OpexProjectSettings()
        settings.project = self.project
        settings.capex_source = 'total_langfactor'
        settings.save()

    def setOpexDefault(self):
        opex = Opex()
        opex.project = self.project
        opex.save()

    def setUtilitiesConstantsDefault(self):
        unity = EquipmentUnity.objects.filter(unity="$/GJ").first()

        for v in DefaultConstants().initialUtilitiesConstans:
            if v["unity"]:
                if v["unity"] == "$/GJ":
                    v["unity"] = unity
                else:
                    v["unity"] = EquipmentUnity.objects.filter(unity=v["unity"]).first()
            else:
                v.pop('unity')
            p = ProjectUtilitiesConstant(**v)
            p.project = self.project
            p.save()

    def updateAllOpexValues(self):

        config = self.checkFieldsUpdate().values()

        MaterialCost(self.project).updateAllCosts()
        self.updateFcilValue(config)
        if config.first()["col_calculated"] is True:
            OperatingLabor(self.project).updateOperatingLabor()
        if config.first()["cut_calculated"] is True:
            UtilityCost(self.project).updateCut()
        if config.first()["wc_calculated"] is True:
            WorkingCapital(self.project).updateWorkingCapital()
        if config.first()["salvage_calculated"] is True:
            opex = Opex.objects.filter(project=self.project).first()
            opex.salvage = round(0.1 * opex.fcil, 2)
            opex.save()
        ManufactoringCost(self.project).updateManufactoringCost()

    def updateFcilValue(self, config):
        if "input" not in config.first()["capex_source"]:
            project = self.project
            opex = Opex.objects.filter(project=self.project).first()
            fcil = getattr(project, config.first()["capex_source"])
            opex.fcil = fcil
            opex.save()

    def checkFieldsUpdate(self, field="all"):
        configs = OpexProjectSettings.objects.filter(project=self.project)
        if field == "all":
            return configs
        else:
            return configs.values(field)

    # Busca e Define as variáveis auxiliares dentro da instância da classe
    def setAuxiliarFactor(self, project):
        self.factors = AuxiliarFactor.objects.filter(project=project).first()

    # Retorna os valores de variáveis auxiliares
    def getConfig(self, project=None):
        if project is not None:
            self.setAuxiliarFactor(project)
            return self.factors
        elif self.factors:
            return self.factors
        else:
            return None


class CostCalculationTools():

    def __init__(self):
        pass

    # apenas juros compostos no momento
    def pmt(tax, n):
        return (tax * ((tax + 1) ** n)) / (((1 + tax) ** n) - 1)

    def costInYear(project, flow, price, flowConversor=1, priceConversor=1):
        """
        ATENTION: all unitys must be already converted and flow must be in HOUR unity
        if can't be done, optional conversor [flowConversor and price Conversor] can
        be set on arguments.
        """
        hourPrice = (flow * flowConversor) * (price * priceConversor)
        hourYear = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year", project=project).first()
        return (hourPrice * hourYear)

    def convertToDefaultUnity(value: float, unity: EquipmentUnity):
        defaultUnity = EquipmentUnity.objects.filter(dimension=unity.dimension, is_default=True).first()
        return ((defaultUnity.convert_factor) / (unity.convert_factor))

    def convertToDesiredUnit(value: float, unity: EquipmentUnity, desired: str):
        # timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        defaultPressureFactor = EquipmentUnity.objects.filter(unity=desired).first()
        conversor = (defaultPressureFactor.convert_factor) / (unity.convert_factor)
        converted = conversor * value
        return (converted)

    def convertEnergyUnity(self, unity: EquipmentUnity, reference: str, value: float):
        defaultPressureFactor = EquipmentUnity.objects.filter(unity=reference).first()
        return ((defaultPressureFactor.convert_factor) / (unity.convert_factor))

    def calculateCost(self, duty: float, utility_cost: float, duty_unity: EquipmentUnity):
        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        valueInGJ = CostCalculationTools.convertEnergyUnity(duty_unity, "GJ", duty)
        return (float(valueInGJ) * float(utility_cost) * (timeWorked.value))

    def calculateAnualCost(value: float, cost_unity: float, value_unity: EquipmentUnity, valueHourUnity='unecessary'):
        """
        value: unit module.
        cost_unity: cost in ($/und)
        value_unit: value unity. Must be a Equipmentunity instance
        hourUnity: default is the value is already converted. Otherwise, fill with the hour base unit(Ex.: 'GJ')
        """

        hourBaseValue = value

        if valueHourUnity != "unecessary":
            hourBaseValue = CostCalculationTools.convertToDesiredUnit(float(value), value_unity, valueHourUnity)

        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        cost = float(hourBaseValue) * float(cost_unity) * (timeWorked.value)
        return (cost)


class CashFlow():
    def __init__(self, project: CapexProject):
        self.project = project

    def calculate(self, depreciation_method: str, depreciation_time: int):
        export_data = {}
        data = self.getData()
        years = list(self.timeInterval(data))
        export_data["years"] = years.copy()
        export_data["investiment"] = self.investiment(data.copy(), years.copy())
        export_data["dk"] = self.dk(data, years.copy(), depreciation_method, depreciation_time)
        self.netProfit(data, years, export_data["dk"])
        export_data["revenue"] = self.revenueValues
        export_data["comd"] = self.comValues
        export_data["netprofit"] = self.netProfitValues
        export_data["CashFlowNonDisconted"] = self.nonDiscountedCF(export_data.copy(), years, data.copy())
        export_data["CashFlowDisconted"] = self.discountedCF(export_data["CashFlowNonDisconted"], years, data["annual_interest_rate"])
        export_data["CumulativeNonDiscontedCF"] = self.cumulativeNonDiscount(export_data["CashFlowNonDisconted"], years)
        export_data["CumulativeDiscontedCF"] = self.cumulativeNonDiscount(export_data["CashFlowDisconted"], years)

        export_data["npv"] = export_data["CumulativeDiscontedCF"][-1]
        export_data["irr"] = round(npf.irr(export_data["CashFlowNonDisconted"]) * 100, 2)
        export_data["pb"] = self.payback(export_data["CashFlowDisconted"])
        return export_data

    def payback(self, cashFlow):
        pbd = 0
        # já que o primeiro ano será zero
        pby = -1
        for cash in cashFlow:
            if cash <= 0:
                v1 = cash
                pby += 1
            else:
                v2 = cash
                pbd = abs((365 * v1) / (v2 - 365))
                break

        return [pby, int(round(pbd, 0))]

    def getData(self):
        opex = Opex.objects.filter(project=self.project).first()
        auxiliate = AuxiliarFactor.objects.filter(project=self.project).first()
        settings = OpexProjectSettings.objects.filter(project=self.project).first()
        data = {
            'fcil': opex.fcil,
            'salvage': opex.salvage,
            'revenue': opex.revenue,
            'com': opex.com,
            'y1': auxiliate.year1,
            'y2': auxiliate.year2,
            'y3': auxiliate.year3,
            'y4': auxiliate.year4,
            'y5': auxiliate.year5,
            'construction_period': settings.construction_period,
            'project_life': settings.project_life,
            'dSL': (1 / settings.project_life),
            'land_cost': settings.land_cost,
            'tax_rate': settings.tax_rate,
            'annual_interest_rate': settings.annual_interest_rate,
            'working_capital': opex.working_capital,
            'tax': settings.tax_rate,
            'annual_interest_rate': settings.annual_interest_rate
        }
        return data

    def timeInterval(self, data):
        years = data["construction_period"] + data["project_life"] + 1
        return (range(years))

    def investiment(self, data, interval):
        investiment = []
        investiment.append(data["land_cost"])
        interval.pop()

        for y in range(data["construction_period"]):
            # Na ultima iteração, acrescentamos o Working Capital
            if y == data["construction_period"] - 1:
                value = data["fcil"] * (data["y" + str(y + 1)])
                value = value + data["working_capital"]
            else:
                value = data["fcil"] * (data["y" + str(y + 1)])

            investiment.append(round(value, 2))
            interval.pop()
        # Após os investimentos iniciais, o valor de investimento é 0
        for i in interval:
            investiment.append(0)
        return investiment

    # taxa de desconto
    def dk(self, data, interval, method, years):
        dk = []
        if method == "MACRS":
            rate = DefaultConstants().macrs
            rate = rate[years]
            for y in interval:
                if y <= data["construction_period"] or len(rate) == 0:
                    dk.append(0)
                else:
                    value = rate[0] * data["fcil"]
                    dk.append(round(value, 2))
                    rate.pop(0)
        elif method == "STR":
            rate = (data["fcil"] - data["salvage"]) / years

            for y in interval:
                if y <= data["construction_period"] or len(rate) == 0:
                    dk.append(0)
                else:
                    value = rate * data["fcil"]
                    dk.append(round(value, 2))
                    rate.pop(0)
        return dk

    def netProfit(self, data, interval, dk):
        revenue = []
        comd = []
        netProfit = []
        for y in interval:
            if y <= data["construction_period"]:
                revenue.append(0)
                comd.append(0)
                netProfit.append(0)
            else:
                revenueValue = data["revenue"]
                comValue = data["com"]
                # (R - COMd - dk)*(1- IRenda) + dk
                value = (revenueValue - comValue - dk[y]) * (1 - data['tax']) + dk[0]
                revenue.append(round(revenueValue, 2))
                comd.append(round(comValue, 2))
                netProfit.append(round(value, 2))
        self.netProfitValues = netProfit
        self.revenueValues = revenue
        self.comValues = comd

    def nonDiscountedCF(self, calculated_data, interval, data):
        ndcf = []
        for y in interval:
            value = calculated_data["netprofit"][y] - calculated_data["investiment"][y]
            ndcf.append(round(value, 2))
        ndcf[-1] = ndcf[-1] + data["working_capital"] + data["land_cost"]
        return ndcf

    def discountedCF(self, ndcf, interval, itax):
        dcf = []
        for y in interval:
            value = ndcf[y] / ((1 + itax)**y)
            dcf.append(round(value, 2))
        return dcf

    def cumulativeDiscounted(self, cFlow, interval):
        cdcf = []
        value = 0
        for y in interval:
            value = value + cFlow[y]
            cdcf.append(round(value, 2))
        return cdcf

    def cumulativeNonDiscount(self, cFlow, interval):
        cndcf = []
        value = 0
        for y in interval:
            value = value + cFlow[y]
            cndcf.append(round(value, 2))
        return cndcf

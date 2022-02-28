from django.db import models


# Create your models here.
class HistoricoFluxoCaixa(models.Model):
    ''' Histórico e previsões de lançamentos no livro caixa da empresa  '''
    descricao = models.CharField(max_length=100)
    valor = models.FloatField()
    data = models.DateField()

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fluxo_caixa_empresa"

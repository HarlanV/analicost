from django.urls import path

from . import views

app_name = 'turton'

urlpatterns = [

    path('', views.index, name='index'),
    path('projeto/<int:project>', views.projectReport_GET, name='project'),
    path('<int:project>/<int:equipamento_id>', views.addEquipmentProjectForm_GET, name='equipment'),
    path('<int:project>/<int:equipamento_id>/POST', views.addEquipmentProject_POST, name='postEquipment'),
    path('createproject', views.createProject, name='createProject'),
    path('createproject/POST', views.createProject, name='postProject'),
    path('getdatacostinfo <int:project>/<int:equipamento_id>', views.equipmentCost, name='calculateCost'),
    path('<int:project>/DELETE', views.deleteProject_DELETE, name='deleteProject'),
    path('<int:project>/<int:equipamento_id>/equipment/DELETE', views.removeEquipment_DELETE, name='removeEquipment'),
    path('<int:project>/<int:equipamento_id>/equipment/edit', views.updateEquipment_GET, name='editEquipment'),
    path('<int:project>/<int:equipamento_id>/equipment/edit/POST', views.updateEquipment_POST, name='updateEquipment'),
    path('<int:equipamento_id><int:unity>/range/GET', views.attributeRange, name='attributerange')
]

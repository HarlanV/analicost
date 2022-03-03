from django.urls import path

from . import views

app_name = 'opex'

urlpatterns = [
    # path('', views.HomeView.index, name='index'),
    path('', views.index, name='index'),
    path('configs/GET', views.ConstantsConfig.index, name='index_config'),
    path('configs/GET/<int:project>', views.ConstantsConfig.formConstants, name='opex_config'),
    path('configs/POST/<int:project>', views.ConstantsConfig.configPOST, name='postConfig'),
    path('material/', views.Material.index, name='index_material'),
    path('material/GET/<int:project>', views.Material.listMaterials, name='opex_material'),
    path('material/create/<int:project>', views.Material.createForm, name='create_material'),
    path('material/create/<int:project>/POST', views.Material.createFormPost, name='material_post'),
    path('material/remove/<int:project>/<int:material>/', views.Material.removeMaterial, name='removeMaterial'),
    # path('datachar', views.HomeView.get_data, name='datachar'),
    # path('capex', views.HomeView.report, name='capex-report'),
]
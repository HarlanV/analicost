from django.urls import path

from . import views

app_name = 'opex'

urlpatterns = [
    path('', views.HomeView.index, name='index'),
    # path('datachar', views.HomeView.get_data, name='datachar'),
    # path('capex', views.HomeView.report, name='capex-report'),

]

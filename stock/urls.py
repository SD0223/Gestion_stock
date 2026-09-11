from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('exporter/excel/', views.exporter_excel, name='exporter_excel'),
    path('exporter/pdf/', views.exporter_pdf, name='exporter_pdf'),  # <-- Nouvelle ligne
]
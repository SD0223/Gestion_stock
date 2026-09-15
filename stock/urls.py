from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('exporter/excel/', views.exporter_excel, name='exporter_excel'),
path('vente/<int:vente_id>/recu/', views.imprimer_recu, name='imprimer_recu'),
    path('exporter/pdf/', views.exporter_pdf, name='exporter_pdf'),  # <-- Nouvelle ligne
path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),

path('pos/', views.pos_index, name='pos_index'),
    path('pos/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('pos/supprimer/<int:produit_id>/', views.supprimer_du_panier, name='supprimer_du_panier'),
    path('pos/valider/', views.valider_vente, name='valider_vente'),]
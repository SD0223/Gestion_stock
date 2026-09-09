from django.contrib import admin
from .models import Categorie, Fournisseur, Produit, MouvementStock

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description')
    search_fields = ('nom',)

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
    search_fields = ('nom', 'email')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_barre', 'categorie', 'prix_vente', 'quantite_stock', 'seuil_alerte')
    list_filter = ('categorie', 'fournisseur')
    search_fields = ('nom', 'code_barre')
    list_editable = ('prix_vente', 'seuil_alerte')

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'type_mouvement', 'quantite', 'date', 'effectue_par')
    list_filter = ('type_mouvement', 'date')
    search_fields = ('produit__nom',)
    readonly_fields = ('date',)
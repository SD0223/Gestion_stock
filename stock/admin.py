from django.contrib import admin
from .models import Categorie, Fournisseur, Produit, MouvementStock, Client, Vente, LigneVente

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Vente, LigneVente

class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1
    fields = ('produit', 'quantite', 'prix_unitaire')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'vendeur', 'statut', 'total', 'date_vente', 'action_imprimer')
    list_filter = ('statut', 'date_vente')
    search_fields = ('client__nom', 'client__telephone', 'id')
    inlines = [LigneVenteInline]
    readonly_fields = ('total', 'date_vente')

    def action_imprimer(self, obj):
        if obj.id:
            url = reverse('imprimer_recu', args=[obj.id])
            return format_html('<a class="button" href="{}" target="_blank">🖨️ Reçu</a>', url)
        return ""
    
    action_imprimer.short_description = "Impression"
# 1. Configuration de la ligne de vente à l'intérieur de la Vente
class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 1  # Nombre de lignes vides affichées par défaut
    fields = ('produit', 'quantite', 'prix_unitaire')
    autocomplete_fields = ['produit']  # Recherche rapide si vous avez beaucoup de produits

# 2. Personnalisation de l'affichage du modèle Vente
@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'vendeur', 'statut', 'total', 'date_vente')
    list_filter = ('statut', 'date_vente')
    search_fields = ('client__nom', 'client__telephone', 'id')
    inlines = [LigneVenteInline]  # Intègre les lignes de vente dans la page de la vente
    readonly_fields = ('date_vente',)

# 3. Personnalisation de l'affichage du modèle Produit (nécessaire pour autocomplete_fields)
@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'categorie', 'prix_vente', 'quantite_stock', 'seuil_alerte')
    list_filter = ('categorie', 'fournisseur')
    search_fields = ('nom', 'code_barre')

# 4. Personnalisation du modèle Client
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'telephone', 'email')
    search_fields = ('nom', 'telephone')

# Enregistrement des autres modèles simples
admin.site.register(Categorie)
admin.site.register(Fournisseur)
admin.site.register(MouvementStock)
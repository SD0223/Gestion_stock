@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'vendeur', 'statut', 'total', 'date_vente')
    list_filter = ('statut', 'date_vente')
    search_fields = ('client__nom', 'client__telephone', 'id')
    inlines = [LigneVenteInline]
    # 'total' est désormais calculé automatiquement
    readonly_fields = ('total', 'date_vente')
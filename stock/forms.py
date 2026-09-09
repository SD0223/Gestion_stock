from django import forms
from .models import MouvementStock, Produit

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'remarque']
        widgets = {
            'produit': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
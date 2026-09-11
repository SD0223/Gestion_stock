from django import forms
from .models import Produit, Fournisseur, MouvementStock

class ProduitForm(forms.ModelForm):
    fournisseur = forms.ModelChoiceField(
        queryset=Fournisseur.objects.all(),
        empty_label="-- Sélectionner un fournisseur --",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    class Meta:
        model = Produit
        fields = '__all__'


class MouvementStockForm(forms.ModelForm):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        empty_label="-- Sélectionner un produit --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = MouvementStock
        fields = ['produit', 'type_mouvement', 'quantite', 'remarque']
        widgets = {
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={'class': 'form-control'}),
            'remarque': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
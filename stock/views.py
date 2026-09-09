from django.shortcuts import render, redirect
from django.db import models
from django.contrib import messages
from .models import Produit, MouvementStock
from .forms import MouvementStockForm

def dashboard(request):
    produits = Produit.objects.all()
    produits_alerte = Produit.objects.filter(quantite_stock__lte=models.F('seuil_alerte'))
    derniers_mouvements = MouvementStock.objects.select_related('produit', 'effectue_par').order_by('-date')[:10]

    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            if request.user.is_authenticated:
                mouvement.effectue_par = request.user
            mouvement.save()
            messages.success(request, "Mouvement de stock enregistré avec succès !")
            return redirect('dashboard')
    else:
        form = MouvementStockForm()

    context = {
        'produits': produits,
        'produits_alerte': produits_alerte,
        'derniers_mouvements': derniers_mouvements,
        'form': form,
    }
    return render(request, 'stock/dashboard.html', context)
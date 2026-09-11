import io
import openpyxl
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import HttpResponse, FileResponse

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Produit, MouvementStock
from .forms import MouvementStockForm


@login_required
def dashboard(request):
    query = request.GET.get('q', '')
    
    if query:
        produits = Produit.objects.filter(nom__icontains=query)
    else:
        produits = Produit.objects.all()

    produits_alerte = Produit.objects.filter(quantite_stock__lte=models.F('seuil_alerte'))
    derniers_mouvements = MouvementStock.objects.select_related('produit', 'effectue_par').order_by('-date')[:10]

    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
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
        'query': query,
    }
    return render(request, 'stock/dashboard.html', context)


@login_required
def exporter_excel(request):
    query = request.GET.get('q', '')
    if query:
        produits = Produit.objects.filter(nom__icontains=query)
    else:
        produits = Produit.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "État du Stock"

    headers = ["Référence", "Nom du Produit", "Prix d'Achat", "Prix de Vente", "Stock Actuel", "Seuil d'Alerte", "Statut"]
    ws.append(headers)

    for col in range(1, len(headers) + 1):
        ws.cell(row=1, column=col).font = openpyxl.styles.Font(bold=True)

    for p in produits:
        statut = "Alerte Stock" if p.quantite_stock <= p.seuil_alerte else "OK"
        ws.append([
            getattr(p, 'reference', 'N/A'),
            p.nom,
            getattr(p, 'prix_achat', 0),
            p.prix_vente,
            p.quantite_stock,
            p.seuil_alerte,
            statut
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = 'attachment; filename="etat_du_stock.xlsx"'
    wb.save(response)

    return response


@login_required
def exporter_pdf(request):
    query = request.GET.get('q', '')
    if query:
        produits = Produit.objects.filter(nom__icontains=query)
    else:
        produits = Produit.objects.all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, alignment=1, spaceAfter=20)
    
    elements.append(Paragraph("Rapport de l'État du Stock", title_style))
    elements.append(Spacer(1, 10))

    data = [["Produit", "Prix Vente", "Stock", "Seuil", "Statut"]]

    for p in produits:
        statut = "Alerte Stock" if p.quantite_stock <= p.seuil_alerte else "OK"
        data.append([
            p.nom,
            f"{p.prix_vente} FCFA",
            str(p.quantite_stock),
            str(p.seuil_alerte),
            statut
        ])

    t = Table(data, colWidths=[180, 100, 70, 70, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#212529")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8F9FA")]),
    ]))

    elements.append(t)
    doc.build(elements)

    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename="etat_du_stock.pdf")
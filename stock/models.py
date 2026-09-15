from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.nom

class Fournisseur(models.Model):
    nom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return self.nom

class Client(models.Model):
    nom = models.CharField(max_length=150)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.telephone})"

class Produit(models.Model):
    nom = models.CharField(max_length=200)
    code_barre = models.CharField(max_length=50, unique=True, blank=True, null=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True)
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.SET_NULL, null=True, blank=True)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)

    def __str__(self):
        return f"{self.nom} (Stock: {self.quantite_stock})"

class Vente(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('PAYE', 'Payé'),
        ('ANNULE', 'Annulé'),
    )
    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)
    vendeur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='PAYE')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Vente #{self.id} - {self.client if self.client else 'Client de passage'}"

class LigneVente(models.Model):
    vente = models.ForeignKey(Vente, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        super().clean()
        if self.produit_id and self.quantite > self.produit.quantite_stock:
            raise ValidationError(
                f"Stock insuffisant pour {self.produit.nom}. Disponible : {self.produit.quantite_stock}"
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.pk:
            self.produit.quantite_stock -= self.quantite
            self.produit.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.quantite} x {self.produit.nom}"

class MouvementStock(models.Model):
    TYPE_MOUVEMENT = (
        ('ENTREE', 'Entrée de stock'),
        ('SORTIE', 'Sortie de stock'),
    )
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT)
    quantite = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now_add=True)
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarque = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        if self.quantite is not None and self.quantite <= 0:
            raise ValidationError({'quantite': "La quantité doit être supérieure à zéro."})
        if self.type_mouvement == 'SORTIE' and self.produit_id:
            if self.quantite > self.produit.quantite_stock:
                raise ValidationError({
                    'quantite': f"Stock insuffisant pour '{self.produit.nom}'. Stock disponible : {self.produit.quantite_stock}."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        if self.type_mouvement == 'ENTREE':
            self.produit.quantite_stock += self.quantite
        elif self.type_mouvement == 'SORTIE':
            self.produit.quantite_stock -= self.quantite
        self.produit.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"
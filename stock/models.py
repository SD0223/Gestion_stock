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

class MouvementStock(models.Model):
    TYPE_MOUVEMENT = (
        ('ENTREE', 'Entrée de stock'),
        ('SORTIE', 'Sortie de stock'),
    )
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements')
    type_mouvement = models.CharField(max_length=10, choices=TYPE_MOUVEMENT)
    quantite = models.PositiveIntegerField()  # Empêche les quantités négatives
    date = models.DateTimeField(auto_now_add=True)
    effectue_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    remarque = models.TextField(blank=True, null=True)

    def clean(self):
        super().clean()
        # 1. Vérification que la quantité est strictement supérieure à zero
        if self.quantite is not None and self.quantite <= 0:
            raise ValidationError({
                'quantite': "La quantité doit être supérieure à zéro."
            })

        # 2. Vérification du stock disponible en cas de sortie
        if self.type_mouvement == 'SORTIE' and self.produit_id:
            if self.quantite > self.produit.quantite_stock:
                raise ValidationError({
                    'quantite': f"Stock insuffisant pour '{self.produit.nom}'. "
                                f"Stock disponible : {self.produit.quantite_stock}, quantité demandée : {self.quantite}."
                })

    def save(self, *args, **kwargs):
        # Exécute la méthode clean() pour forcer le contrôle de validation
        self.full_clean()

        # Mise à jour du stock seulement après validation
        if self.type_mouvement == 'ENTREE':
            self.produit.quantite_stock += self.quantite
        elif self.type_mouvement == 'SORTIE':
            self.produit.quantite_stock -= self.quantite
        
        self.produit.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type_mouvement} - {self.produit.nom} ({self.quantite})"
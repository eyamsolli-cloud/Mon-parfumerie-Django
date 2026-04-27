from django.db import models
from django.urls import reverse


# ──────────────────────────────
#  MARQUE
# ──────────────────────────────
class Marque(models.Model):
    nom    = models.CharField('Marque', max_length=100)
    pays   = models.CharField('Pays d\'origine', max_length=100, blank=True)
    logo   = models.ImageField('Logo', upload_to='marques/', blank=True, null=True)

    class Meta:
        ordering      = ['nom']
        verbose_name  = 'Marque'
        verbose_name_plural = 'Marques'

    def __str__(self):
        return self.nom


# ──────────────────────────────
#  PARFUM
# ──────────────────────────────
class Parfum(models.Model):
    GENRE_CHOICES = [
        ('femme',  'Femme'),
        ('homme',  'Homme'),
        ('mixte',  'Mixte'),
    ]

    nom         = models.CharField('Nom du parfum', max_length=200)
    marque      = models.ForeignKey(Marque, on_delete=models.CASCADE,
                                    related_name='parfums',
                                    verbose_name='Marque')
    genre       = models.CharField('Genre', max_length=10, choices=GENRE_CHOICES)
    description = models.TextField('Description', blank=True)
    prix        = models.DecimalField('Prix (TND)', max_digits=8, decimal_places=2)
    volume_ml   = models.PositiveIntegerField('Volume (ml)', default=100)
    stock       = models.PositiveIntegerField('Stock disponible', default=0)
    image       = models.ImageField('Image', upload_to='parfums/', blank=True, null=True)
    date_ajout  = models.DateTimeField(auto_now_add=True)
    date_modif  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering     = ['nom']
        verbose_name = 'Parfum'
        verbose_name_plural = 'Parfums'

    def __str__(self):
        return f"{self.nom} – {self.marque}"

    def get_absolute_url(self):
        return reverse('parfums:detail', kwargs={'pk': self.pk})

    @property
    def en_stock(self):
        return self.stock > 0


# ──────────────────────────────
#  CLIENT
# ──────────────────────────────
class Client(models.Model):
    nom       = models.CharField('Nom', max_length=100)
    prenom    = models.CharField('Prénom', max_length=100)
    email     = models.EmailField('Email', unique=True)
    telephone = models.CharField('Téléphone', max_length=20, blank=True)
    adresse   = models.TextField('Adresse', blank=True)
    date_inscription = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering     = ['nom', 'prenom']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_absolute_url(self):
        return reverse('parfums:client_detail', kwargs={'pk': self.pk})

    @property
    def total_commandes(self):
        return self.commandes.count()

    @property
    def total_depense(self):
        from django.db.models import Sum
        result = self.commandes.aggregate(total=Sum('parfum__prix'))
        return result['total'] or 0


# ──────────────────────────────
#  COMMANDE
# ──────────────────────────────
class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee',  'Confirmée'),
        ('livree',     'Livrée'),
        ('annulee',    'Annulée'),
    ]

    client     = models.ForeignKey(Client, on_delete=models.CASCADE,
                                   related_name='commandes',
                                   verbose_name='Client')
    parfum     = models.ForeignKey(Parfum, on_delete=models.CASCADE,
                                   related_name='commandes',
                                   verbose_name='Parfum')
    quantite   = models.PositiveIntegerField('Quantité', default=1)
    statut     = models.CharField('Statut', max_length=20,
                                  choices=STATUT_CHOICES, default='en_attente')
    date_commande = models.DateTimeField('Date de commande', auto_now_add=True)
    notes      = models.TextField('Notes', blank=True)

    class Meta:
        ordering     = ['-date_commande']
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'

    def __str__(self):
        return f"Commande #{self.pk} — {self.client} → {self.parfum.nom}"

    @property
    def prix_total(self):
        return self.parfum.prix * self.quantite

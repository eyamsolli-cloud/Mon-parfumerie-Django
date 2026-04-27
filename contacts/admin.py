from django.contrib import admin
from .models import Marque, Parfum, Client, Commande


@admin.register(Marque)
class MarqueAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'pays']
    search_fields = ['nom']


@admin.register(Parfum)
class ParfumAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'marque', 'genre', 'prix', 'stock']
    list_filter   = ['genre', 'marque']
    search_fields = ['nom']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'prenom', 'email', 'telephone', 'date_inscription']
    search_fields = ['nom', 'prenom', 'email']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display  = ['pk', 'client', 'parfum', 'quantite', 'statut', 'date_commande']
    list_filter   = ['statut']
    search_fields = ['client__nom', 'parfum__nom']
    list_editable = ['statut']

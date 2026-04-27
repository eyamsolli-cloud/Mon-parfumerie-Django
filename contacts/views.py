from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from .models import Parfum, Marque, Client


# ═══════════════════════════════
#  AUTHENTIFICATION
# ═══════════════════════════════

def connexion(request):
    """Vue pour la connexion utilisateur"""
    if request.user.is_authenticated:
        return redirect('parfums:list')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username} !')
                next_url = request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                return redirect('parfums:list')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
        else:
            messages.error(request, 'Veuillez remplir tous les champs.')

    return render(request, 'parfums/connexion.html')


def inscription(request):
    """Vue pour l'inscription utilisateur"""
    if request.user.is_authenticated:
        return redirect('parfums:list')

    if request.method == 'POST':
        username  = request.POST.get('username', '').strip()
        email     = request.POST.get('email', '').strip()
        password  = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not all([username, email, password, password2]):
            messages.error(request, 'Tous les champs sont obligatoires.')
        elif password != password2:
            messages.error(request, 'Les mots de passe ne correspondent pas.')
        elif len(password) < 6:
            messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Cet email est déjà utilisé.')
        else:
            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                login(request, user)
                messages.success(request, f'Bienvenue {username} ! Votre compte a été créé avec succès.')
                return redirect('parfums:list')
            except Exception as e:
                messages.error(request, f'Erreur lors de la création du compte : {e}')

    return render(request, 'parfums/inscription.html')


def deconnexion(request):
    """Vue pour la déconnexion"""
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Vous avez été déconnecté avec succès.')
    return redirect('parfums:list')


@login_required
def profil(request):
    """Vue du profil utilisateur"""
    user = request.user
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        new_pass   = request.POST.get('new_password', '')
        new_pass2  = request.POST.get('new_password2', '')

        if email and email != user.email:
            if User.objects.filter(email=email).exclude(pk=user.pk).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
                return redirect('parfums:profil')
            user.email = email

        user.first_name = first_name
        user.last_name  = last_name

        if new_pass:
            if new_pass != new_pass2:
                messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
                return redirect('parfums:profil')
            if len(new_pass) < 6:
                messages.error(request, 'Le mot de passe doit contenir au moins 6 caractères.')
                return redirect('parfums:profil')
            user.set_password(new_pass)
            messages.success(request, 'Mot de passe modifié. Veuillez vous reconnecter.')
            user.save()
            logout(request)
            return redirect('parfums:connexion')

        user.save()
        messages.success(request, 'Profil mis à jour avec succès.')
        return redirect('parfums:profil')

    # Stats pour le profil
    context = {
        'nb_parfums': Parfum.objects.count(),
        'nb_marques': Marque.objects.count(),
        'nb_clients': Client.objects.count(),
    }
    return render(request, 'parfums/profil.html', context)


# ── Helper : ajoute les classes Bootstrap aux widgets ──
def _bootstrap_form(form):
    for field in form.fields.values():
        widget = field.widget
        css = widget.attrs.get('class', '')
        name = widget.__class__.__name__
        if name in ('Select', 'NullBooleanSelect'):
            widget.attrs['class'] = (css + ' form-select').strip()
        elif name == 'Textarea':
            widget.attrs['class'] = (css + ' form-control').strip()
            widget.attrs.setdefault('rows', 3)
        elif name == 'CheckboxInput':
            widget.attrs['class'] = (css + ' form-check-input').strip()
        else:
            widget.attrs['class'] = (css + ' form-control').strip()
    return form


# ═══════════════════════════════
#  PARFUMS
# ═══════════════════════════════

class ParfumListView(ListView):
    model               = Parfum
    template_name       = 'parfums/Parfum_list.html'
    context_object_name = 'parfums'
    paginate_by         = 9

    def get_queryset(self):
        qs     = super().get_queryset().select_related('marque')
        q      = self.request.GET.get('q', '')
        genre  = self.request.GET.get('genre', '')
        marque = self.request.GET.get('marque', '')
        sort   = self.request.GET.get('sort', 'nom')

        if q:
            qs = qs.filter(
                Q(nom__icontains=q) |
                Q(marque__nom__icontains=q) |
                Q(description__icontains=q)
            )
        if genre:
            qs = qs.filter(genre=genre)
        if marque:
            qs = qs.filter(marque_id=marque)

        order_map = {
            'prix_asc':  'prix',
            'prix_desc': '-prix',
            'nom':       'nom',
            'recent':    '-date_ajout',
        }
        return qs.order_by(order_map.get(sort, 'nom'))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['marques']      = Marque.objects.all()
        ctx['q']            = self.request.GET.get('q', '')
        ctx['genre_actif']  = self.request.GET.get('genre', '')
        ctx['marque_actif'] = self.request.GET.get('marque', '')
        ctx['sort_actif']   = self.request.GET.get('sort', 'nom')
        return ctx


class ParfumDetailView(DetailView):
    model               = Parfum
    template_name       = 'parfums/parfums_detail.html'
    context_object_name = 'parfum'


class ParfumCreateView(LoginRequiredMixin, CreateView):
    model         = Parfum
    fields        = ['nom', 'marque', 'genre', 'description',
                     'prix', 'volume_ml', 'stock', 'image']
    template_name = 'parfums/parfums_form.html'
    success_url   = reverse_lazy('parfums:list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class ParfumUpdateView(LoginRequiredMixin, UpdateView):
    model         = Parfum
    fields        = ['nom', 'marque', 'genre', 'description',
                     'prix', 'volume_ml', 'stock', 'image']
    template_name = 'parfums/parfums_form.html'
    success_url   = reverse_lazy('parfums:list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class ParfumDeleteView(LoginRequiredMixin, DeleteView):
    model               = Parfum
    template_name       = 'parfums/parfum_confirm_delete.html'
    context_object_name = 'parfum'
    success_url         = reverse_lazy('parfums:list')
    login_url           = '/connexion/'


# ═══════════════════════════════
#  MARQUES
# ═══════════════════════════════

class MarqueListView(ListView):
    model               = Marque
    template_name       = 'parfums/marque_list.html'
    context_object_name = 'marques'


class MarqueCreateView(LoginRequiredMixin, CreateView):
    model         = Marque
    fields        = ['nom', 'pays', 'logo']
    template_name = 'parfums/marque_forme.html'
    success_url   = reverse_lazy('parfums:marque_list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class MarqueUpdateView(LoginRequiredMixin, UpdateView):
    model         = Marque
    fields        = ['nom', 'pays', 'logo']
    template_name = 'parfums/marque_forme.html'
    success_url   = reverse_lazy('parfums:marque_list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class MarqueDeleteView(LoginRequiredMixin, DeleteView):
    model               = Marque
    template_name       = 'parfums/marque_confirm_delete.html'
    context_object_name = 'marque'
    success_url         = reverse_lazy('parfums:marque_list')
    login_url           = '/connexion/'


# ═══════════════════════════════
#  CLIENTS
# ═══════════════════════════════

class ClientListView(LoginRequiredMixin, ListView):
    model               = Client
    template_name       = 'parfums/client_list.html'
    context_object_name = 'clients'
    paginate_by         = 10
    login_url           = '/connexion/'

    def get_queryset(self):
        qs = super().get_queryset()
        q  = self.request.GET.get('q', '')
        if q:
            qs = qs.filter(
                Q(nom__icontains=q) |
                Q(prenom__icontains=q) |
                Q(email__icontains=q) |
                Q(telephone__icontains=q)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['q'] = self.request.GET.get('q', '')
        return ctx


class ClientDetailView(LoginRequiredMixin, DetailView):
    model               = Client
    template_name       = 'parfums/client_detail.html'
    context_object_name = 'client'
    login_url           = '/connexion/'


class ClientCreateView(LoginRequiredMixin, CreateView):
    model         = Client
    fields        = ['nom', 'prenom', 'email', 'telephone', 'adresse']
    template_name = 'parfums/client_form.html'
    success_url   = reverse_lazy('parfums:client_list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model         = Client
    fields        = ['nom', 'prenom', 'email', 'telephone', 'adresse']
    template_name = 'parfums/client_form.html'
    success_url   = reverse_lazy('parfums:client_list')
    login_url     = '/connexion/'

    def get_form(self, form_class=None):
        return _bootstrap_form(super().get_form(form_class))


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model               = Client
    template_name       = 'parfums/client_confirm_delete.html'
    context_object_name = 'client'
    success_url         = reverse_lazy('parfums:client_list')
    login_url           = '/connexion/'


# ═══════════════════════════════
#  COMMANDES
# ═══════════════════════════════
from .models import Commande

def commande_list(request):
    """Liste globale de toutes les commandes"""
    commandes = Commande.objects.select_related('client', 'parfum', 'parfum__marque').all()
    q = request.GET.get('q', '')
    if q:
        from django.db.models import Q
        commandes = commandes.filter(
            Q(client__nom__icontains=q) |
            Q(client__prenom__icontains=q) |
            Q(parfum__nom__icontains=q)
        )
    return render(request, 'parfums/commande_list.html', {
        'commandes': commandes,
        'q': q,
    })


def commande_client(request, pk):
    """Toutes les commandes d'un client précis"""
    client    = get_object_or_404(Client, pk=pk)
    commandes = Commande.objects.filter(client=client).select_related('parfum', 'parfum__marque')
    return render(request, 'parfums/commande_client.html', {
        'client':    client,
        'commandes': commandes,
    })


@login_required
def commande_ajouter(request, client_pk=None):
    """Créer une nouvelle commande"""
    client_initial = get_object_or_404(Client, pk=client_pk) if client_pk else None

    if request.method == 'POST':
        client_id  = request.POST.get('client')
        parfum_id  = request.POST.get('parfum')
        quantite   = request.POST.get('quantite', 1)
        statut     = request.POST.get('statut', 'en_attente')
        notes      = request.POST.get('notes', '')

        try:
            client   = Client.objects.get(pk=client_id)
            parfum   = Parfum.objects.get(pk=parfum_id)
            quantite = int(quantite)
            if quantite < 1:
                raise ValueError

            Commande.objects.create(
                client=client,
                parfum=parfum,
                quantite=quantite,
                statut=statut,
                notes=notes,
            )
            messages.success(request, f'Commande ajoutée pour {client} — {parfum.nom}.')
            return redirect('parfums:commande_client', pk=client.pk)
        except (Client.DoesNotExist, Parfum.DoesNotExist):
            messages.error(request, 'Client ou parfum introuvable.')
        except (ValueError, TypeError):
            messages.error(request, 'Quantité invalide (doit être ≥ 1).')

    return render(request, 'parfums/commande_form.html', {
        'clients':        Client.objects.all().order_by('nom'),
        'parfums':        Parfum.objects.all().select_related('marque').order_by('nom'),
        'statuts':        Commande.STATUT_CHOICES,
        'client_initial': client_initial,
    })


@login_required
def commande_modifier(request, pk):
    """Modifier le statut d'une commande"""
    commande = get_object_or_404(Commande, pk=pk)

    if request.method == 'POST':
        statut   = request.POST.get('statut', commande.statut)
        quantite = request.POST.get('quantite', commande.quantite)
        notes    = request.POST.get('notes', commande.notes)
        try:
            commande.quantite = int(quantite)
            commande.statut   = statut
            commande.notes    = notes
            commande.save()
            messages.success(request, 'Commande mise à jour.')
        except (ValueError, TypeError):
            messages.error(request, 'Quantité invalide.')
        return redirect('parfums:commande_client', pk=commande.client.pk)

    return render(request, 'parfums/commande_modifier.html', {
        'commande': commande,
        'statuts':  Commande.STATUT_CHOICES,
    })


@login_required
def commande_supprimer(request, pk):
    """Supprimer une commande"""
    commande  = get_object_or_404(Commande, pk=pk)
    client_pk = commande.client.pk
    if request.method == 'POST':
        commande.delete()
        messages.success(request, 'Commande supprimée.')
        return redirect('parfums:commande_client', pk=client_pk)
    return render(request, 'parfums/commande_supprimer.html', {'commande': commande})

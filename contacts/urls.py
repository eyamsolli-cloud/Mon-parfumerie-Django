from django.urls import path
from . import views

app_name = 'parfums'

urlpatterns = [
    # ── Accueil ──
    path('', views.ParfumListView.as_view(), name='list'),

    # ── Authentification ──
    path('connexion/',   views.connexion,   name='connexion'),
    path('inscription/', views.inscription, name='inscription'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/',      views.profil,      name='profil'),

    # ── Parfums ──
    path('parfum/ajouter/',            views.ParfumCreateView.as_view(), name='add'),
    path('parfum/<int:pk>/',           views.ParfumDetailView.as_view(), name='detail'),
    path('parfum/<int:pk>/modifier/',  views.ParfumUpdateView.as_view(), name='edit'),
    path('parfum/<int:pk>/supprimer/', views.ParfumDeleteView.as_view(), name='delete'),

    # ── Marques ──
    path('marques/',                       views.MarqueListView.as_view(),   name='marque_list'),
    path('marques/ajouter/',               views.MarqueCreateView.as_view(), name='marque_create'),
    path('marques/<int:pk>/modifier/',     views.MarqueUpdateView.as_view(), name='marque_update'),
    path('marques/<int:pk>/supprimer/',    views.MarqueDeleteView.as_view(), name='marque_delete'),

    # ── Clients ──
    path('clients/',                    views.ClientListView.as_view(),   name='client_list'),
    path('clients/ajouter/',            views.ClientCreateView.as_view(), name='client_add'),
    path('clients/<int:pk>/',           views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<int:pk>/modifier/',  views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/supprimer/', views.ClientDeleteView.as_view(), name='client_delete'),

    # ── Commandes ──
    path('commandes/',                              views.commande_list,      name='commande_list'),
    path('commandes/ajouter/',                      views.commande_ajouter,   name='commande_ajouter'),
    path('commandes/client/<int:pk>/',              views.commande_client,    name='commande_client'),
    path('commandes/client/<int:client_pk>/ajouter/', views.commande_ajouter, name='commande_ajouter_client'),
    path('commandes/<int:pk>/modifier/',            views.commande_modifier,  name='commande_modifier'),
    path('commandes/<int:pk>/supprimer/',           views.commande_supprimer, name='commande_supprimer'),
]

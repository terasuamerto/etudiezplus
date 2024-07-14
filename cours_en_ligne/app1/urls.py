from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views_api import UserProfileViewSet, SubscriptionViewSet, CoursViewSet, LeconViewSet


urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('inscription/', views.inscription, name='inscription'),
    path('verify_code/', views.verify_code, name='verify_code'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profile/', views.profile, name='profile'),
    path('subscription/', views.subscription, name='subscription'),
    path('subscribe_standard/', views.subscribe_standard, name='subscribe_standard'),
    path('subscribe_premium/', views.subscribe_premium, name='subscribe_premium'),
    path('success_payment/',views.success_payment,name='success_payment'),
    #Changement
    path('liste_cours/', views.liste_cours, name='liste_cours'),
    path('liste_cours_niveau/<int:niveau>/', views.liste_cours_niveau, name="liste_cours_niveau"),
    path('infos_cours/<int:id>/', views.infos_cours, name='infos_cours'),
    path('details_cours/<int:id>/<int:lecon>/', views.details_cours, name='details_cours'),
    path('image/<int:id>/', views.image,name='image'),
    path('pdfcours/<int:lecon>/', views.affiche_pdf,name='pdfcours'),
    path('videocours/<int:lecon>/', views.affiche_video,name='videocours'),
    path('pdf_ressource_lecon/<int:id>/',views.affiche_pdf_ressource,name="pdf_ressource_lecon"),
    path('video_ressource_cours/<int:id>/',views.affiche_video_ressource,name="video_ressource_cours"),
    path('lien_ressource/<int:id>/',views.lien_ressource,name="lien_ressource_cours"),
    path('affiche_lecon/',views.afficher_lecon,name='affiche_lecon'),
    path('likes/',views.like, name='likes_cours'),
    path('inscription_cours',views.inscription, name="inscription_cours"),


    #url pour la page admin enseignant
    path('admin_page_enseignant/',views.admin_page_enseignant, name="admin_page_enseignant"),
    path('liste_element/<str:element>/',views.liste_element,name='liste_element'),
    path('liste_cours_enseignant/',views.liste_cours_enseignant, name="liste_cours_enseignant"),
    path('liste_lecon_enseignant/',views.liste_lecon_enseignant, name="liste_lecon_enseignant"),
    path('liste_ressource_enseignant/',views.liste_ressource_enseignant, name="liste_ressource_enseignant"),
    path('liste_grands_points_enseignant/',views.liste_grands_points_enseignant, name="liste_grands_points_enseignant"),
    path('liste_inscription_cours_enseignant/',views.liste_inscription_cours_enseignant,name="liste_inscription_cours_enseignant"),


    #ajout cours
    path('page_create_cours_enseignant/',views.page_create_cours_enseignant,name="page_create_cours_enseignant"),
    path('add_cours_enseignant/',views.add_cours_enseignant,name="add_cours_enseignant"),
    path('page_create_grands_points_enseignant/<int:coursId>/',views.page_create_grands_points_enseignant,name="page_create_grands_points_enseignant"),
    path('create_grands_points_enseignant/<int:coursId>/',views.create_grands_points_enseignant,name="create_grands_points_enseignant")



    #Api
]


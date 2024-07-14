from django.core.mail import send_mail
from django.contrib import admin
from .models import *
admin.site.register(UserProfile)
admin.site.register([Matiere,Niveau,Cours,Lecon,Ressource,GrandsPoint,Inscription])


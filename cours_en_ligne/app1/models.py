from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone
from tinymce.models import HTMLField
from django.core.validators import FileExtensionValidator
from django.db.models.signals import pre_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tel = models.CharField(max_length=8, unique=True)
    is_enseignant = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

#Soubscription pour un abonnement
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=100)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

#Payement 
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50)
    token = models.CharField(max_length=255, blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_id} - {self.status}"



class Matiere(models.Model):
    id = models.AutoField(primary_key=True)
    intitule = models.CharField(max_length=30)
    class Meta:
        db_table = "Matiere"
        verbose_name_plural = "Matieres"
        ordering = ["intitule"]

    def __str__(self):
        return f"{self.intitule}"

class Niveau(models.Model):
    id = models.IntegerField(primary_key=True)
    intitule = models.CharField(max_length=30)

    class Meta:
        verbose_name_plural = "Niveaux"
        db_table = "Niveau"
        ordering = ["intitule"]

    def __str__(self):
        return f"{self.intitule}"
    
class Cours(models.Model):
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    vues = models.PositiveBigIntegerField(default=0)
    likes = models.PositiveBigIntegerField(default=0)
    instructeur = models.ForeignKey(UserProfile,on_delete=models.CASCADE,related_name="instructeur_cours")
    niveau = models.ForeignKey(Niveau,on_delete=models.CASCADE,related_name="niveau_cours")
    matiere= models.ForeignKey(Matiere,on_delete=models.CASCADE,related_name="matiere_cours")
    prerequis = models.CharField(max_length=255,default="aucune connaissance nécessaire")
    estimation = models.CharField(max_length=255,default="9 heures pour terminer le cours")
    detail_estimation =  models.CharField(max_length=255,default="3 semaines à 3 heures par semaine")
    a_propos = models.CharField(max_length=511,default="description du cours")
    image = models.ImageField(upload_to='images_upload', default="image1.jpeg")

    class Meta:
        db_table = "Cours"
        verbose_name_plural = "cours"
        ordering = ["titre"]

    def __str__(self):
        return f"{self.titre}"



class Lecon(models.Model):
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('texte', 'TEXTE'),
        ('video', 'VIDEO'),
    ]

    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=255)
    num_ordre = models.IntegerField(default=0)
    type_de_contenu = models.CharField(max_length=5, choices=TYPE_CHOICES)
    contenu_texte = HTMLField (default="contenu", editable=True)
    contenu_pdf = models.FileField(upload_to='pdf/',default='fichier.pdf', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    contenu_video = models.FileField(upload_to='videos/', default='video.mp4', validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    description = models.CharField(max_length=255)
    likes = models.PositiveBigIntegerField(default=0)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="cours_lecon",blank=True,null=True)
    class Meta:
        db_table = "Lecon"
        ordering = ["titre"]

    def __str__(self):
        return f"{self.titre}"


class Ressource(models.Model):
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('lien', 'LIEN HYPERTEXTE'),
        ('video', 'VIDEO'),
    ]
    id = models.AutoField(primary_key=True)
    titre = models.CharField(max_length=30)
    type_de_contenu = models.CharField(max_length=5, choices=TYPE_CHOICES)
    contenu_pdf = models.FileField(upload_to='pdf/', default='fichier.pdf', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    contenu_video = models.FileField(upload_to='videos/', default='video.mp4',validators=[FileExtensionValidator(allowed_extensions=['mp4'])])
    contenu_lien = models.URLField(max_length=200)
    lecon = models.ForeignKey(Lecon, on_delete=models.CASCADE, related_name="lecon_cours",blank=True,null=True)

    class Meta:
        db_table = "Ressource"
        ordering = ["titre"]

    def __str__(self):
        return f"{self.titre}"

class GrandsPoint(models.Model):
    id = models.AutoField(primary_key=True)
    contenu_texte =  models.TextField(default="contenu") #HTMLField (default="contenu", editable=True)
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="grandsp_cours")

    class Meta:
        db_table = "GrandsPoint"
        ordering = ["id"]

    def __str__(self):
        return f"{self.id}"


class Inscription(models.Model):
    eleve = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="eleve_inscription")
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name="cours_inscription")
    id = models.CharField(max_length=255, primary_key=True, default="valeur")
    date_inscription = models.DateTimeField(auto_now=True)


    class Meta:
        db_table = "Inscription"
        ordering = ["id"]

    def __str__(self):
        return f"{self.id}"


    def save(self, *args, **kwargs):
        self.id = (f"{self.cours}_{self.eleve}")
        super(Inscription, self).save(*args, **kwargs)


# @receiver(pre_save, sender=Inscription)
# def set_inscription_id(sender, instance, *args, **kwargs):
#     print(instance.cours)
#     instance.id = f"{instance.cours}_{instance.eleve}"


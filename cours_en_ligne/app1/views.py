import random
import json
import requests
import os
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime, timedelta
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils.timezone import make_aware
from django.utils.crypto import get_random_string
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import FileResponse
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.utils.timezone import now
# Import error code dictionaries
from .error_codes import PAYIN_ERROR_CODES
from .decorateur import etat_user


def accueil(request):
    return render(request, 'accueil.html')

def inscription(request):
    if request.method == 'POST':
        user_data = {
            'nom': request.POST['nom'],
            'prenom': request.POST['prenom'],
            'username': request.POST['username'],
            'email': request.POST['email'],
            'tel': request.POST['tel'],
            'password': request.POST['password'],
        }


        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=user_data['username']).exists():
            context = {
                'errorInscription': True,
                'message': 'Ce nom d\'utilisateur est déjà utilisé.',
            }
            return render(request, 'inscription.html', context)
        
        if User.objects.filter(email=user_data['email']).exists():
            context = {
                'errorInscription': True,
                'message': 'Cet email est déjà utilisé.',
            }
            return render(request, 'inscription.html', context)
        
        # Vérifier si l'utilisateur existe déjà avec ce numéro de téléphone
        try:
            existing_user = UserProfile.objects.get(tel=user_data['tel'][5:].strip())
            context = {
                'errorInscription': True,
                'message': 'Ce numéro de téléphone est déjà utilisé.',
            }
            return render(request, 'inscription.html', context)
        except UserProfile.DoesNotExist:
            pass

        # Vérifier que le numéro de téléphone a exactement 8 chiffres après "+226"
        if not user_data['tel'].startswith('+226 '):
            context = {
                'errorInscription': True,
                'message': 'Le numéro de téléphone doit commencer par "+226".',
            }
            return render(request, 'inscription.html', context)

        # Enlever le préfixe "+226 " pour compter les chiffres seulement
        num_digits = len(user_data['tel'][5:].strip())  # Enlève "+226 " et enlève les espaces de début/fin
        if num_digits != 8 or not user_data['tel'][5:].strip().isdigit():
            context = {
                'errorInscription': True,
                'message': 'Le numéro de téléphone doit comporter exactement 8 chiffres après "+226".',
            }
            return render(request, 'inscription.html', context)

        # Vérifier que le mot de passe a au moins 8 caractères
        if len(user_data['password']) < 8:
            context = {
                'errorInscription': True,
                'message': 'Le mot de passe doit contenir au moins 8 caractères.',
            }
            return render(request, 'inscription.html', context)

        # Générer un code de vérification avec expiration
        verification_code = random.randint(100000, 999999)
        expires_at = datetime.now() + timedelta(seconds=120)  # Expiration dans 120 secondes
        expires_at_str = expires_at.strftime('%Y-%m-%d %H:%M:%S')
        request.session['verification_code'] = {
            'code': verification_code,
            'expires_at': expires_at_str,  # Stocker en tant que chaîne formatée
        }
        request.session['user_data'] = user_data

        # Calculer le temps restant avant l'expiration
        time_remaining = expires_at - datetime.now()

        # Envoyer un email avec le code de vérification et le temps restant
        send_mail(
            'Code de verification',
            f'Votre code de vérification est {verification_code}. Ce code expirera dans {time_remaining.seconds} secondes.',
            'erasuamert@gmail.com',
            [user_data['email']],
            fail_silently=False,
        )

        messages.success(request, 'Un code de vérification a été envoyé à votre adresse e-mail.')
        return redirect('verify_code')

    return render(request, 'inscription.html')

def verify_code(request):
    if request.method == 'POST':
        entered_code = request.POST['verification_code']
        verification_code = request.session.get('verification_code', {}).get('code')
        expires_at_str = request.session.get('verification_code', {}).get('expires_at')

        if not verification_code or not expires_at_str:
            messages.error(request, 'Code de vérification expiré. Veuillez recommencer.')
            return redirect('inscription')

        # Vérifier si le code est expiré
        expires_at = datetime.strptime(expires_at_str, '%Y-%m-%d %H:%M:%S')
        if datetime.now() > expires_at:
            messages.error(request, 'Code de vérification expiré. Veuillez recommencer.')
            return redirect('inscription')

        # Comparer le code entré avec le code stocké en session
        if entered_code == str(verification_code):
            # Code correct, enregistrer l'utilisateur
            user_data = request.session.get('user_data')

            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['prenom'],
                last_name=user_data['nom']
            )

            tel_without_prefix = user_data['tel'][5:].strip()
            UserProfile.objects.create(user=user, tel=tel_without_prefix)

            authenticated_user = authenticate(request, username=user_data['username'], password=user_data['password'])
            login(request, authenticated_user)

            messages.success(request, 'Votre compte a été créé avec succès.')
            return redirect('subscription')
        else:
            messages.error(request, 'Code de vérification incorrect. Veuillez réessayer.')
            return render(request, 'verify_code.html')

    return render(request, 'verify_code.html')

def connexion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        tel = request.POST.get('tel')
        password = request.POST.get('password')

        user = None
        username = None

        if email:
            try:
                user = User.objects.get(email=email)
                username = user.username
            except User.DoesNotExist:
                user = None

        elif tel:
            if not tel.startswith('+226 '):
                context = {
                    'errorLogin': True,
                    'message': 'Le numéro de téléphone doit commencer par "+226 ".',
                }
                return render(request, 'connexion.html', context)

            tel_without_prefix = tel[5:].strip()
            try:
                user_profile = UserProfile.objects.get(tel=tel_without_prefix)
                user = user_profile.user
                username = user.username
            except UserProfile.DoesNotExist:
                user = None

        if user:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not Subscription.objects.filter(user=user, end_date__gt=datetime.now()).exists():
                    messages.error(request, 'Votre abonnement a expiré. Veuillez vous réabonner.')
                    return redirect('subscription')
                login(request, user)
                return redirect('liste_cours')
            else:
                context = {
                    'errorLogin': True,
                    'message': 'Identifiants ou mot de passe incorrects.',
                }
                return render(request, 'connexion.html', context)
        else:
            # Si ni l'email ni le numéro de téléphone ne sont trouvés
            context = {
                'errorLogin': True,
                'message': 'Identifiants incorrects. Veuillez vérifier vos informations et réessayer.',
            }
            return render(request, 'connexion.html', context)

    return render(request, 'connexion.html')

def deconnexion(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/')
def subscription(request):
    return render(request, 'subscription.html')

@login_required(login_url='/')
def subscribe_standard(request):
    return create_payment(request)

@login_required(login_url='/')
def subscribe_premium(request):
    return create_payment(request)

@csrf_exempt
def create_payment(request):
    user = request.user
    transaction_id = f'ETDP{get_random_string(8)}{now().strftime("%Y%m%d%H%M%S")}'
    amount = 100 if request.path == "/subscribe_standard/" else 150

    response = payin_with_redirection(transaction_id, amount)

    if response.get("response_code") == "00":
        token = response.get("token")
        redirect_url = response.get("response_text")
        
        # Enregistrement du paiement en attente avec le jeton
        Payment.objects.create(
            user=user,
            transaction_id=transaction_id,
            amount=amount,
            status="pending",
            token=token  # 
        )
        request.session['transaction_id'] = transaction_id
        return redirect(redirect_url)
    else:
        error_code = response.get("response_code")
        error_message = f"response_code={error_code}<br><br>"
        error_message += f"response_text={response.get('response_text')}<br><br>"
        error_message += f"description={response.get('description')}<br><br>"
        return handle_error(error_code)
    
def payin_with_redirection(transaction_id, amount):
    url = "https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/create"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "commande": {
            "invoice": {
                "items": [
                    {
                        "name": "cours",
                        "description": "cours des eleves",
                        "quantity": 1,
                        "unit_price": str(amount),
                        "total_price": str(amount)
                    }
                ],
                "total_amount": str(amount),
                "devise": "XOF",
                "description": "cours des eleves du lycee",
                "customer": "",
                "customer_firstname": "Prenom du client",
                "customer_lastname": "Nom du client",
                "customer_email": "erasuamert@gmail.com"
            },
            "store": {
                "name": "webapp",
                "website_url": "https://appweb.com"
            },
            "actions": {
                "cancel_url": "http://127.0.0.1:8000/cancel_payment/",
                "return_url": "http://localhost:8000/success_payment/",
                "callback_url": "http://localhost:8000/success_payment/"
            },
            "custom_data": {
                "transaction_id": transaction_id
            }
        }
    }
    response = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    return response.json()


@csrf_exempt
def success_payment(request):
    transaction_id = request.session.get('transaction_id')
    if transaction_id:
        payment = Payment.objects.get(transaction_id=transaction_id)
        payment_data = check_payment_status_with_api(payment.token)

        if payment_data.get("status") == "completed":  # Si le paiement est confirmé
            payment.status = "completed"
            payment.save()
            user = request.user
            plan = 'standard' if payment.amount==100 else 'premium' 
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30)  # Abonnement d'un mois

            # Créer ou mettre à jour l'abonnement pour l'utilisateur
            subscription, created = Subscription.objects.get_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'start_date': start_date,
                    'end_date': end_date
                }
            )

            if not created:
                # Si l'abonnement existe déjà, mettez à jour les champs
                subscription.plan = plan
                subscription.start_date = start_date
                subscription.end_date = end_date
                subscription.save()

            return HttpResponse("Paiement effectue avec succes !!!!!")
        else:
            messages.error(request, 'Le paiement n\'a pas été confirmé. Veuillez réessayer.')
            return redirect('subscription')
    else:
        messages.error(request, 'Erreur de transaction. Veuillez réessayer.')
        return redirect('subscription')
    
def check_payment_status_with_api(token):
    url = f"https://app.ligdicash.com/pay/v01/redirect/checkout-invoice/confirm/?invoiceToken={token}"
    headers = {
        "Apikey": "MAGPMLT3QFJLIPUDN",
        "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZF9hcHAiOjE1MDA5LCJpZF9hYm9ubmUiOjg5OTQyLCJkYXRlY3JlYXRpb25fYXBwIjoiMjAyNC0wNC0wOCAwODozMjoyNCJ9.NRcyHfFO8OyaXOaklZ2DJ2Arf-gV8OXGfMIELQzdw88",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    try:
        response = requests.get(url, headers=headers, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error occurred: {errh}")
        return {"error": "HTTP Error", "message": str(errh)}
    except requests.exceptions.RequestException as err:
        print(f"Request Exception occurred: {err}")
        return {"error": "Request Exception", "message": str(err)}
        
def handle_error(error_code):
    error_description = PAYIN_ERROR_CODES.get(error_code, "Unknown error")
    return HttpResponse(f"Error Code: {error_code}, Description: {error_description}")

def cancel_payment(request):
    return render(request, 'cancel_payment.html', {"message": "Echec de paiement."})

@login_required(login_url='/')
def profile(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)
    subscription = Subscription.objects.filter(user=user).order_by('-start_date').first()
    
    context = {
        'user': user,
        'user_profile': user_profile,
        'subscription': subscription,
    }

    if request.method == 'POST':
        user.first_name = request.POST['first_name']
        user.last_name = request.POST['last_name']
        user.username = request.POST['username']
        user.email = request.POST['email']
        
        # Mettre à jour le profil utilisateur avec le numéro de téléphone
        phone = request.POST['phone']
        if phone.startswith('+226 ') and len(phone[5:].strip()) == 8:
            user_profile.tel = phone[5:].strip()
        else:
            messages.error(request, 'Le numéro de téléphone doit commencer par "+226" et comporter exactement 8 chiffres après.')

        # Changer le mot de passe si les champs sont remplis
        password = request.POST.get('password')
        if password:
            if len(password) < 8:
                messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
            else:
                user.set_password(password)
                messages.success(request, 'Votre mot de passe a été changé avec succès.')

        user.save()
        user_profile.save()
        messages.success(request, 'Vos informations ont été mises à jour avec succès.')
        return render(request, 'profile.html', context)

    return render(request, 'profile.html', context)


#affiche la galerie des cours
@login_required(login_url='/')
def liste_cours(request):
    allLevels = Niveau.objects.all().order_by('-id')
    #allCours = (Cours.objects.all())
    allCours = []

    for level in allLevels:
        cours = Cours.objects.filter(niveau=level)[:10]

        allCours.append({
            'niveau':level,
            'cours':cours
        })

    context = {
        'allCours': allCours,
    }

    return render(request,'card_view.html',context)




#effiche le cours du niveau concerne
@login_required(login_url='/')
def liste_cours_niveau(request,niveau):
    allLevels = Niveau.objects.filter(id=niveau)
    #allCours = (Cours.objects.all())
    allCours = []

    for level in allLevels:
        cours = Cours.objects.filter(niveau=level)

        allCours.append({
            'niveau':level,
            'cours':cours
        })

    context = {
        'allCours': allCours,
    }

    return render(request,'card_view.html',context)


#retourne l'image associee a un cours
@login_required(login_url='/')
def image(request,id):
    cours = Cours.objects.get(pk=id)
    img = cours.image.name.replace("images/media/", "")
    chemin = os.path.join(settings.MEDIA_ROOT,img)
    
    response = FileResponse(open(chemin, 'rb'))
    return response

#renvoie une description plus detaillee du cours choisi
@login_required(login_url='/')
def infos_cours(request,id):
    print(request)
    cours = Cours.objects.get(pk=id)
    cours.vues =  cours.vues +1
    cours.save()
    grandP = GrandsPoint.objects.filter(cours__id=id).values()
    inscrit = Inscription.objects.filter(id__startswith=f"{cours.titre}_").count()



    context = {'cours': cours,
            'allGrandsPoints':grandP,
               'nbreinscrit':inscrit}
    return render(request, "infos_cours.html",context)


#retourne la page proprement dite du cours
@login_required(login_url='/')
def details_cours(request,id,lecon):
    

    leconId = lecon


    #recuperation du cours
    cours = Cours.objects.get(pk=id)

    #recuperation de toutes les lecons du cours
    allLecons = Lecon.objects.filter(cours__id=id).order_by('num_ordre').values()
    
    #par defaut, la premiere lecon est affichee sur la page
    lecon = allLecons[lecon-1]

    #recuperation des ressources de la lecon 1
    ressources = Ressource.objects.filter(lecon__id=leconId).values()
    
    context = {
        'cours':cours,
        'allLecons':allLecons,
        'lecon':lecon,
        'allRessources':ressources
    }
    return render(request,'details_cours.html',context)

#renvoie le fichier pdf representant le contenu principal de la lecon
@require_GET
@login_required(login_url='/')
def affiche_pdf(request,lecon):
    lecon_affiche = Lecon.objects.get(pk=lecon)
    chemin = f"{settings.MEDIA_ROOT}/{str(lecon_affiche.contenu_pdf)}"

    response = FileResponse(open(chemin, 'rb'),content_type='application/pdf')
    return response

#retourne la video du contenu du cours
@login_required(login_url='/')
def affiche_video(request,lecon):
    lecon_afficher = Lecon.objects.get(pk=lecon)
    chemin = f"{settings.MEDIA_ROOT}/{str(lecon_afficher.contenu_video)}"
    print(f"videos: {chemin}")
    response = FileResponse(open(chemin, 'rb'),content_type='video/mp4')
    return response
    

#affiche la lecon choisie sur la page detail cours
@require_POST
@login_required(login_url='/')
def afficher_lecon(request):
    resultat = {}
    leconId = request.POST.get("lecon")
    try:
        lecon_affiche = (Lecon.objects.get(pk=leconId))
        resultat['message'] = 'succes'
        resultat['id'] = lecon_affiche.id
        resultat['num'] = lecon_affiche.num_ordre
        resultat['titre'] = lecon_affiche.titre
        resultat['type_contenu'] = lecon_affiche.type_de_contenu
        if lecon_affiche.type_de_contenu == "texte":
            resultat['contenu'] = lecon_affiche.contenu_texte
        elif lecon_affiche.type_de_contenu == "pdf":
            chemin = f"{settings.MEDIA_ROOT}/{str(lecon_affiche.contenu_pdf)}"
            print(chemin)
            resultat['contenu'] = chemin
        else:
            resultat['contenu'] = f"{settings.MEDIA_ROOT}/{str(lecon_affiche.contenu_video)}"
        
        resultat['likes'] = lecon_affiche.likes

        
        
        return JsonResponse((resultat))
    except Lecon.ObjectDoesNotExist:
        resultat['message'] = 'echec'
        resultat['donnees'] = 'none'
        return JsonResponse(resultat)




@require_POST
@login_required(login_url='/')
def like(request):
    resultat = {}
    coursId = request.POST.get("cours")
    print(coursId)
    try:
        cours = Cours.objects.get(pk=coursId)

        cours.likes = cours.likes + 1
        cours.save()
        resultat['donnees'] = cours.likes
        return JsonResponse(resultat)
    except Cours.ObjectDoesNotExist:
        resultat['donnees'] = 'none'
        return JsonResponse(resultat)
    

# inscription d'un eleve à une cours
@require_POST
@login_required(login_url='/')
def inscription_cours(request):
    resultat={}
    eleveId = request.user.id
    coursId = request.POST.get("coursid")
    try:
        cours = Cours.objects.get(id=coursId)
        eleve = UserProfile.objects.get(id=eleveId)
        if Inscription.objects.filter(eleve=eleve, cours=cours).exists():
            resultat["status"] = "succes"
            resultat["message"] = "Déjà inscrit(e) au cours"
            return JsonResponse(resultat)
        inscription = Inscription(
            eleve=eleve,
            cours= cours,
            date_inscription=datetime.now())
        inscription.save()
        
        resultat["status"] = "succes"
        resultat["message"] = "RAS"
        return JsonResponse(resultat)
    
    except Cours.DoesNotExist:
        resultat["status"] = "echec"
        resultat["message"] = "erreur cours"
        return JsonResponse(resultat)
    except UserProfile.DoesNotExist:
        resultat["status"] = "echec"
        resultat["message"] = "erreur user"
        return JsonResponse(resultat)

# gestion des fichiers ressources


#renvoie le fichier pdf contenu dans les ressources d'une lecon
@require_GET
@login_required(login_url='/')
def affiche_pdf_ressource(request,id):

    #id correspond à l'id du pdf
    pdf_affiche = Ressource.objects.get(pk=id)
    chemin = f"{settings.MEDIA_ROOT}/{str(pdf_affiche.contenu_pdf)}"

    #faire les verifications avant de retourner le pdf
    #response = {"resultat":"none"}
    response = FileResponse(open(chemin, 'rb'),content_type='application/pdf')
    return (response)
    # response = {"resultat":"none"}
    # return JsonResponse(response)




#retourne la video contenu dans les ressources du cours
@login_required(login_url='/')
def affiche_video_ressource(request,id):

    video_afficher = Ressource.objects.get(pk=id)
    chemin = f"{settings.MEDIA_ROOT}/{str(video_afficher.contenu_video)}"
    print(f"videos: {chemin}")
    response = FileResponse(open(chemin, 'rb'),content_type='video/mp4')
    return response
    # response = {"resultat":"none"}
    # return JsonResponse(response)



#retourne le lien hypertexte des fichiers ressources
@login_required(login_url='/')
def lien_ressource(request,id):
    ressource = Ressource.objects.get(pk=id)
    lien = ressource.contenu_lien
    resultat = {
        'statut':'ok',
        'lien': lien
        }
    return JsonResponse(resultat)


#page d'administration de l'enseignant
@etat_user
@login_required(login_url='/')
def admin_page_enseignant(request):
    allMatieres = Matiere.objects.all()
    allNiveau = Niveau.objects.all()

    
    return render(request,'admin/page_admin_base_enseignant.html')



#concerne les matieres et les niveaux
@etat_user
@login_required(login_url='/')
def liste_element(request,element):
    context= {}
    chemin = request.path.replace("/liste_","")
    print(chemin)
    if element=="matiere":
        allMatieres = Matiere.objects.all()
        context = {
            'table':'Matières',
            'elements':allMatieres
        }
    elif element=="niveau":
        allNiveau = Niveau.objects.all().order_by('-id')
        context = {
            'table':'Niveaux',
            'elements':allNiveau
        }
        
    return render(request,'admin/liste_element.html',context)


#retourne tous les cours crees par l'enseignant connecte
@etat_user
@login_required(login_url='/')
def liste_cours_enseignant(request):
    id_enseignant = request.user.id
    allCours = Cours.objects.filter(instructeur__id=id_enseignant).order_by('id')
    for cours in allCours:

        print(cours)
    context={
        'allCours':allCours
    }
    return render(request,'admin/liste_cours_enseignant.html',context)



#retourne toutes les lecon creees par l'enseignant connecte
@etat_user
@login_required(login_url='/')
def liste_lecon_enseignant(request):
    id_enseignant = request.user.id
    allLecon = Lecon.objects.filter(cours__instructeur__id=id_enseignant).order_by('id')
    context = {
        'allLecon':allLecon
    }
    return render(request,'admin/liste_lecon_enseignant.html',context)


#retourne toutes les ressources ajoutées par l'enseignant connecte
@etat_user
@login_required(login_url='/')
def liste_ressource_enseignant(request):
    id_enseignant = request.user.id
    allRessource = Ressource.objects.filter(lecon__cours__instructeur__id=id_enseignant).order_by('id')

    context = {
        'allRessource':allRessource
    }
    return render(request,'admin/liste_ressource_enseignant.html',context)



#retourne tous les grands points ajoutés par l'enseignant connecte
@etat_user
@login_required(login_url='/')
def liste_grands_points_enseignant(request):
    id_enseignant = request.user.id
    allGrandsPoints = GrandsPoint.objects.filter(cours__instructeur__id=id_enseignant).order_by('id')

    context = {
        'allGrandsPoints':allGrandsPoints
    }

    return render(request,'admin/liste_grands_points_enseignant.html',context)



#retourne toutes les inscriptions au cours de l'enseignant connecte
@etat_user
@login_required(login_url='/')
def liste_inscription_cours_enseignant(request):
    id_enseignant = request.user.id
    allInscription = Inscription.objects.filter(cours__instructeur__id=id_enseignant).order_by('id')

    context = {
        'allInscription':allInscription
    }

    return render(request,'admin/liste_inscription_cours_enseignant.html',context)



#retourne la page permettant d'ajouter un cours complet avec les lecons, grands points et fichiers ressources
@etat_user
@login_required(login_url='/')
def page_create_cours_enseignant(request):
    allNiveau = Niveau.objects.all().order_by('id')
    allMatiere = Matiere.objects.all().order_by('id')
    context ={
        'from_cours':True,   #il sera utilise pour l'affichage de certains boutons dans le template
        'allNiveau':allNiveau,
        'allMatiere':allMatiere,
    }
    return render(request,'admin/cours.html', context)

#ajoutee un cours
@etat_user
@login_required(login_url='/')
@require_POST
def add_cours_enseignant(request):
    titre = request.POST["titre"]
    description = request.POST["description"]
    niveau = request.POST["niveau"]
    matiere = request.POST["matiere"]
    prerequis = request.POST["prerequis"]
    estimation = request.POST["estimation"]
    detail_estimation = request.POST["detail_estimation"]
    a_propos = request.POST["a_propos"]
    image = request.FILES.get("image")


    enseignant = UserProfile.objects.get(pk=request.user.id)
    niveau = Niveau.objects.get(id=niveau)  
    matiere = Matiere.objects.get(id=matiere)

    cours = Cours.objects.create(
        titre=titre,
        description=description,
        niveau=niveau,
        matiere=matiere,
        prerequis=prerequis,
        estimation=estimation,
        detail_estimation=detail_estimation,
        a_propos=a_propos,
        image=image,
        instructeur=enseignant

    )
    cours.save()
    resultat = {
        'success': True,
        'message': 'cours ajoute',
        'coursId':cours.id}

    return JsonResponse(resultat)


#retourne la page d'ajout de grand point
@etat_user
@login_required(login_url='/')
def page_create_grands_points_enseignant(request,coursId):

    cours = Cours.objects.filter(pk=coursId)
    context = {
        'Cours':cours
    }
    return render(request,'admin/grands_points.html',context)


#ajoute un grand point dans le processus d'ajout de cours
@etat_user
@login_required(login_url='/')
def create_grands_points_enseignant(request,coursId):
    # print(request.POST)
    contenu = ''
    titre = request.POST["titre"]
    type_contenu = request.POST["type_contenu"]
    coursId = request.POST["cours"]
    cours = Cours.objects.get(pk=coursId)


    if type_contenu == "pdf":
        contenu = request.FILES.get('file')

        grandPoint = GrandsPoint.objects.create(

        )
    elif type_contenu == "video":
        contenu = request.FILES.get('file')
    elif type_contenu == "lien":
        contenu = request.POST["contenu"]



    resultat = {
            'success': True,
            'message': 'grand ajoute',
            }
    return JsonResponse(resultat)



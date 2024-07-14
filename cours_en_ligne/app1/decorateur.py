from django.shortcuts import render
from .models import UserProfile




#ce decorateur permet de verifier si l'utilisateur est un enseignant
def etat_user(vue_fonc):
    def _vue_developpe(request, *args, **kwargs):
        id = request.user.id
        try:
            user = UserProfile.objects.get(pk=id)
            if user.is_enseignant:
                return vue_fonc(request, *args, **kwargs)
            else:
                return render(request, 'accueil.html')
        except UserProfile.DoesNotExist:
            return render(request, 'accueil.html')
    return _vue_developpe
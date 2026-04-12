from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from django.shortcuts import redirect
from django.http import HttpResponse

# Vue simple de redirection (sans requête HTTP externe)
def redirect_to_frontend(request):
    # URL de ton frontend Expo (web)
    frontend_url = "http://localhost:8081/accueil"
    return redirect(frontend_url)

# Vue d'erreur si le frontend ne répond pas (optionnel)
def frontend_unavailable(request):
    return HttpResponse(
        """
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #CE1021;">Front-end non détecté</h1>
            <p style="font-size: 18px;">Le serveur Django est OK, mais votre React Native ne répond pas sur le port 8081.</p>
            <div style="background: #f4f4f4; padding: 15px; display: inline-block; border-radius: 5px; text-align: left;">
                <code>1. Ouvrez votre terminal frontend</code><br>
                <code>2. Tapez: <b>npx expo start</b> (ou npm start)</code><br>
                <code>3. Appuyez sur <b>w</b> pour le web ou lancez l'émulateur</code>
            </div>
            <br><br>
            <a href="/admin/" style="color: #003399; text-decoration: none; font-weight: bold;">← Retourner à l'Admin Django</a>
        </div>
        """,
        content_type="text/html"
    )

urlpatterns = [
    # Redirection de la racine vers le frontend
    path('', redirect_to_frontend),
    path('accueil', redirect_to_frontend),
    path('admin/', admin.site.urls),
    path('api/', include('src.urls')),
]

# Servir les fichiers média en mode développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
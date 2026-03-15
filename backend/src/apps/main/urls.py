from django.urls import include, path
import src.apps.main.routes.auth_routes as auth_routes

app_name = 'main'

urlpatterns = [
    path('auth/', include(auth_routes)),
]
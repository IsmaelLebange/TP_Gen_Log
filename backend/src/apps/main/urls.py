from django.urls import include, path
import src.apps.main.api.routes.auth_routes as auth_routes

app_name = 'main'

urlpatterns = [
    path('auth/', include(auth_routes)),
    path('token/', include('src.apps.main.api.routes.token_routes')),
]
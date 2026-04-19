from django.urls import path
from .views import registro_usuario

urlpatterns = [
    path('registro/', registro_usuario, name='registro'),
]
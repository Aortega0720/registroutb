from django.contrib import admin
from .models import Perfil


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):

    list_display = ('user', 'identificacion')
    search_fields = ('identificacion', 'user__email', 'user__username')
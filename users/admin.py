from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Campos que aparecem na listagem do admin
    list_display = ('email', 'name', 'usertype', 'is_staff', 'is_superuser')
    list_filter = ('usertype', 'is_staff', 'is_superuser', 'is_active')

    # Campos de pesquisa
    search_fields = ('email', 'name', 'cnpj', 'phone')
    ordering = ('email',)

    # Campos que aparecem ao criar/editar usuário
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações pessoais'), {'fields': ('name', 'phone', 'cnpj', 'categoria', 'descricao', 'logo', 'fotos', 'usertype')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    # Campos para criação de um novo usuário
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'usertype', 'is_staff', 'is_superuser'),
        }),
    )

    # Permite editar a senha dentro do admin
    filter_horizontal = ('groups', 'user_permissions',)

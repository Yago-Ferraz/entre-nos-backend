from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import User, Empresa, FotoEmpresa

# --- USER ADMIN ---
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'name', 'usertype','is_active', 'is_staff', 'is_superuser')
    list_filter = ('usertype', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'name', 'phone')
    ordering = ('email',) 

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Informações pessoais'), {'fields': ('name', 'phone', 'usertype')}),
        (_('Permissões'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Datas importantes'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2', 'usertype', 'is_staff', 'is_superuser'),
        }),
    )

    filter_horizontal = ('groups', 'user_permissions',)


# --- FOTO EMPRESA INLINE ---
class FotoEmpresaInline(admin.TabularInline):
    model = FotoEmpresa
    extra = 1
    readonly_fields = ('preview',)

    def preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="height: 80px;"/>', obj.imagem.url)
        return "-"
    preview.short_description = "Pré-visualização"


# --- EMPRESA ADMIN ---
@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('user', 'categoria', 'meta', 'avaliacao', 'logo_preview')
    list_filter = ('categoria',)
    search_fields = ('user__name', 'user__email')
    inlines = [FotoEmpresaInline]

    fieldsets = (
        (None, {
            'fields': ('user', 'categoria', 'descricao', 'logo', 'logo_preview')
        }),
        ('Métricas', {
            'fields': ('meta', 'avaliacao')
        }),
    )

    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height: 100px;"/>', obj.logo.url)
        return "-"
    logo_preview.short_description = "Logo"

# --- FOTO EMPRESA ADMIN ---
@admin.register(FotoEmpresa)
class FotoEmpresaAdmin(admin.ModelAdmin):
    list_display = ('empresa', 'imagem_preview')
    search_fields = ('empresa__user__name',)

    readonly_fields = ('imagem_preview',) 

    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" style="height: 80px;"/>', obj.imagem.url)
        return "-"
    imagem_preview.short_description = "Pré-visualização"

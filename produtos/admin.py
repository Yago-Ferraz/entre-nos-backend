from django.contrib import admin
from django.utils.html import format_html
from .models import Produto

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'nome',
        'descricao',
        'preco',
        'quantidade',
        'imagem_preview',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
        'empresa'
    )
    readonly_fields = (
        'id',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    )
    search_fields = ('nome', 'descricao')
    list_filter = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('nome', 'descricao', 'preco', 'quantidade', 'imagem', 'empresa')
        }),
        ('Informações de Sistema', {
            'fields': ('id', 'created_at', 'created_by', 'updated_at', 'updated_by')
        }),
    )

    def get_queryset(self, request):
        # Pré-carrega os usuários relacionados para não ficar None
        qs = super().get_queryset(request)
        return qs.select_related('created_by', 'updated_by')

    @admin.display(description='Imagem')
    def imagem_preview(self, obj):
        if obj.imagem:
            return format_html('<img src="{}" width="50" height="50" />', obj.imagem.url)
        return "-"

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

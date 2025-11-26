from django.contrib import admin
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

    def imagem_preview(self, obj):
        if obj.imagem:
            return f'<img src="{obj.imagem.url}" width="50" height="50" />'
        return "-"
    imagem_preview.allow_tags = True
    imagem_preview.short_description = 'Imagem'

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

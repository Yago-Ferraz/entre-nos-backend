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
        'criador_nome',
        'created_at',
        'updated_at',
        'created_by_nome',
        'updated_by_nome',
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
            'fields': ('nome', 'descricao', 'preco', 'quantidade', 'imagem')
        }),
        ('Informações de Sistema', {
            'fields': ('id', 'created_at', 'updated_at', 'created_by', 'updated_by')
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

    def criador_nome(self, obj):
        # Retorna o nome do usuário ou o ID caso não exista
        if obj.created_by:
            return obj.created_by.name
        return obj.created_by_id or "-"
    criador_nome.short_description = 'Criador'

    def created_by_nome(self, obj):
        if obj.created_by:
            return obj.created_by.name
        return obj.created_by_id or "-"
    created_by_nome.short_description = 'Criado por'

    def updated_by_nome(self, obj):
        if obj.updated_by:
            return obj.updated_by.name
        return obj.updated_by_id or "-"
    updated_by_nome.short_description = 'Atualizado por'

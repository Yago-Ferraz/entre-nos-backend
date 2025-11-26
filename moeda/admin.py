from django.contrib import admin
from .models import Carteira, Transacao

class TransacaoInline(admin.TabularInline):
    """Permite visualizar e adicionar transações diretamente na página da carteira."""
    model = Transacao
    extra = 0  # Não mostrar formulários de transação extra por padrão
    readonly_fields = ('tipo_ativo', 'tipo_operacao', 'valor', 'valor_movimentado', 'descricao', 'created_at')
    can_delete = False  # Transações não devem ser deletadas
    ordering = ('-created_at',)

    def has_add_permission(self, request, obj=None):
        # Desabilita a adição de novas transações a partir do inline
        return False

@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    """Admin customizado para o modelo Carteira."""
    list_display = ('empresa', 'saldo_dinheiro', 'saldo_moeda', 'atualizado_em')
    readonly_fields = ('saldo_dinheiro', 'saldo_moeda', 'atualizado_em')
    search_fields = ('empresa__user__name', 'empresa__user__email')
    inlines = [TransacaoInline]

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    """Admin customizado para o modelo Transacao."""
    list_display = ('carteira', 'tipo_operacao', 'tipo_ativo', 'valor_movimentado', 'descricao', 'created_at', 'created_by', 'updated_at', 'updated_by')
    list_filter = ('tipo_operacao', 'tipo_ativo', 'created_at', 'created_by', 'updated_by')
    search_fields = ('carteira__empresa__user__name', 'descricao')
    readonly_fields = ('carteira', 'tipo_operacao', 'tipo_ativo', 'valor', 'valor_movimentado', 'descricao', 'created_at', 'created_by', 'updated_at', 'updated_by') # Added 'descricao', 'created_by', 'updated_at', 'updated_by'

    fieldsets = (
        (None, {
            'fields': ('carteira',)
        }),
        ('Detalhes da Transação', {
            'fields': ('tipo_operacao', 'tipo_ativo', 'valor', 'valor_movimentado', 'descricao',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by',)
        }),
    )

    def has_add_permission(self, request):
        # Transações são criadas via lógica de negócio, não manualmente no admin
        return False

    def save_model(self, request, obj, form, change):
        if not change: # Only set created_by on creation
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)
from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from .models import Carteira, Transacao

class TransacaoInline(admin.TabularInline):
    """Permite visualizar e adicionar transações diretamente na página da carteira."""
    model = Transacao
    extra = 0  # Não mostrar formulários de transação extra por padrão
    readonly_fields = ('tipo_ativo', 'tipo_operacao', 'valor', 'valor_movimentado', 'descricao', 'created_at')
    can_delete = False  # Transações não devem ser deletadas
    ordering = ('-created_at',)



@admin.register(Carteira)
class CarteiraAdmin(admin.ModelAdmin):
    """Admin customizado para o modelo Carteira."""
    list_display = ('empresa', 'saldo_dinheiro', 'saldo_moeda', 'atualizado_em')
    readonly_fields = ('atualizado_em',)
    search_fields = ('empresa__user__name', 'empresa__user__email')
    inlines = [TransacaoInline]

@admin.register(Transacao)
class TransacaoAdmin(admin.ModelAdmin):
    """Admin customizado para o modelo Transacao."""
    list_display = ('carteira', 'tipo_operacao', 'tipo_ativo', 'valor_movimentado', 'descricao', 'created_at', 'created_by', 'updated_at', 'updated_by')
    list_filter = ('tipo_operacao', 'tipo_ativo', 'created_at', 'created_by', 'updated_by')
    search_fields = ('carteira__empresa__user__name', 'descricao')
    readonly_fields = ('valor_movimentado', 'created_at', 'created_by', 'updated_at', 'updated_by')

    fieldsets = (
        (None, {
            'fields': ('carteira',)
        }),
        ('Detalhes da Transação', {
            'fields': ('tipo_operacao', 'tipo_ativo', 'valor', 'descricao',)
        }),
        ('Auditoria', {
            'fields': ('created_at', 'created_by', 'updated_at', 'updated_by',)
        }),
    )

    def has_change_permission(self, request, obj=None):
        # Permite adicionar, mas não alterar transações existentes
        if obj is not None:
            return False
        return super().has_change_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if not change: # Only process new transactions
            carteira = form.cleaned_data['carteira']
            valor = form.cleaned_data['valor']
            tipo_ativo = form.cleaned_data['tipo_ativo']
            tipo_operacao = form.cleaned_data['tipo_operacao']
            descricao = form.cleaned_data.get('descricao', '')

            try:
                carteira.registrar_operacao(
                    valor=valor,
                    tipo_ativo=tipo_ativo,
                    tipo_operacao=tipo_operacao,
                    descricao=descricao,
                    user=request.user
                )
                messages.success(request, "Transação criada e saldo da carteira atualizado com sucesso.")
            except ValidationError as e:
                messages.error(request, f"Erro ao criar transação: {e}")
                # Prevent default save by returning
                return
            except Exception as e:
                messages.error(request, f"Ocorreu um erro inesperado: {e}")
                return
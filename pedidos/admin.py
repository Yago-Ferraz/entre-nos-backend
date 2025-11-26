from django.contrib import admin
from .models import Pedido, ItemPedido
from produtos.models import Produto
from users.models import User


# ============================
# INLINE DOS ITENS DO PEDIDO
# ============================
class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 1
    fields = ("produto", "quantidade", "preco_unitario", "subtotal_preview")
    readonly_fields = ("preco_unitario", "subtotal_preview")

    def subtotal_preview(self, obj):
        """Mostra o subtotal na linha"""
        if obj.id:
            return obj.subtotal()
        return "—"

    subtotal_preview.short_description = "Subtotal"


# ============================
# ADMIN DO PEDIDO
# ============================
@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "usuario", "status", "valor_total", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("id", "usuario__name", "usuario__email")
    readonly_fields = ("valor_total", "created_at", "updated_at")

    inlines = [ItemPedidoInline]

    # Recalcula o total quando itens são salvos
    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        form.instance.atualizar_total()
        return instances

    # Recalcula o total ao salvar o pedido diretamente
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        obj.atualizar_total()


# ============================
# ADMIN DO ITEM DO PEDIDO (CASO VOCÊ QUEIRA VER NA LISTA)
# ============================
@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "pedido", "produto", "quantidade", "preco_unitario", "subtotal")
    search_fields = ("pedido__id", "produto__nome")
    list_filter = ("produto",)

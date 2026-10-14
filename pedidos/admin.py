
from decimal import Decimal

from django.contrib import admin
from .models import Categoria, Produto, Pedido, ItemPedido


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome',)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'preco', 'disponivel')
    list_filter = ('categoria', 'disponivel')
    search_fields = ('nome',)


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'nome_cliente', 'status',
        'valor_total', 'data_criacao'
    )
    list_filter = ('status', 'data_criacao')
    search_fields = ('nome_cliente', 'telefone_cliente')
    inlines = [ItemPedidoInline]

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)

        pedido = form.instance
        total = sum(
            (item.subtotal() for item in pedido.itens.all()),
            Decimal('0.00')
        )

        pedido.valor_total = total
        pedido.save(update_fields=['valor_total'])


admin.site.register(ItemPedido)

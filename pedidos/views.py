
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal

from .models import Produto, Pedido, ItemPedido, Categoria


def cardapio(request):
    categorias = Categoria.objects.prefetch_related('produtos').all()

    return render(
        request,
        'pedidos/cardapio.html',
        {'categorias': categorias}
    )


def adicionar_ao_carrinho(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id, disponivel=True)
    carrinho = request.session.get('carrinho', {})
    chave = str(produto_id)

    if chave in carrinho:
        carrinho[chave]['quantidade'] += 1
    else:
        carrinho[chave] = {
            'nome': produto.nome,
            'preco': str(produto.preco),
            'quantidade': 1,
        }

    request.session['carrinho'] = carrinho
    messages.success(request, f'{produto.nome} adicionado ao carrinho.')
    return redirect('cardapio')


def ver_carrinho(request):
    carrinho = request.session.get('carrinho', {})
    itens = []
    total = Decimal('0.00')

    for produto_id, dados in carrinho.items():
        preco = Decimal(dados['preco'])
        subtotal = preco * dados['quantidade']
        total += subtotal
        itens.append({
            'produto_id': produto_id,
            'nome': dados['nome'],
            'preco': preco,
            'quantidade': dados['quantidade'],
            'subtotal': subtotal,
        })

    return render(request, 'pedidos/carrinho.html', {'itens': itens, 'total': total})


def remover_do_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', {})
    chave = str(produto_id)

    if chave in carrinho:
        del carrinho[chave]
        request.session['carrinho'] = carrinho

    return redirect('ver_carrinho')


def finalizar_pedido(request):
    carrinho = request.session.get('carrinho', {})

    if not carrinho:
        messages.warning(request, 'Seu carrinho está vazio.')
        return redirect('cardapio')

    if request.method == 'POST':
        nome = request.POST.get('nome_cliente')
        telefone = request.POST.get('telefone_cliente')
        endereco = request.POST.get('endereco_entrega')

        total = Decimal('0.00')
        for dados in carrinho.values():
            total += Decimal(dados['preco']) * dados['quantidade']

        pedido = Pedido.objects.create(
            nome_cliente=nome,
            telefone_cliente=telefone,
            endereco_entrega=endereco,
            valor_total=total,
        )

        for produto_id, dados in carrinho.items():
            produto = get_object_or_404(Produto, id=produto_id)
            ItemPedido.objects.create(
                pedido=pedido,
                produto=produto,
                quantidade=dados['quantidade'],
                preco_unitario=Decimal(dados['preco']),
            )

        request.session['carrinho'] = {}
        return render(request, 'pedidos/pedido_confirmado.html', {'pedido': pedido})

    return redirect('ver_carrinho')


def acompanhar_pedido(request):
    pedido = None

    if request.method == 'POST':
        pedido_id = request.POST.get('pedido_id')
        pedido = Pedido.objects.filter(id=pedido_id).first()

        if not pedido:
            messages.error(request, 'Pedido não encontrado.')

    return render(request, 'pedidos/acompanhar.html', {'pedido': pedido})

# cart/views.py — AutoMotors
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from garagem.models import Veiculo
from acessorios.models import Acessorio
from home.models import HistoricoInteresse
from home.decorators import ssl_required


@ssl_required
@login_required
def add_to_cart(request, item_id):
    cart, created = Cart.objects.get_or_create(user=request.user)
    item_type = None
    actual_item = None

    if 'veiculo' in request.resolver_match.url_name:
        item_type = 'garagem'
        actual_item = get_object_or_404(Veiculo, id=item_id)
    elif 'acessorio' in request.resolver_match.url_name:
        item_type = 'acessorio'
        actual_item = get_object_or_404(Acessorio, id=item_id)

    if not actual_item:
        # Lidar com erro ou redirecionar
        return redirect(request.META.get('HTTP_REFERER', '/'))

    cart_item = None
    if item_type == 'garagem':
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            veiculo_item=actual_item,
            acessorio_item=None,
            defaults={'price_at_purchase': actual_item.preco}
        )
    elif item_type == 'acessorio':
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            veiculo_item=None,
            acessorio_item=actual_item,
            defaults={'price_at_purchase': actual_item.preco}
        )

    if not item_created:
        cart_item.quantity += 1
    cart_item.price_at_purchase = actual_item.preco
    cart_item.save()

    # Persiste histórico permanente quando for um carro da garagem
    if item_type == 'garagem':
        hist, hist_created = HistoricoInteresse.objects.get_or_create(
            user=request.user,
            veiculo_item=actual_item,
            defaults={
                'nome_snapshot': actual_item.nome,
                'preco_snapshot': actual_item.preco,
                'foto_snapshot': actual_item.foto.url if actual_item.foto else '',
            },
        )
        if not hist_created:
            hist.vezes_marcado += 1
            hist.nome_snapshot = actual_item.nome
            hist.preco_snapshot = actual_item.preco
            hist.foto_snapshot = actual_item.foto.url if actual_item.foto else hist.foto_snapshot
            hist.save()

    return redirect('cart:view_cart')



@ssl_required
@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    context = {'cart': cart}
    return render(request, 'cart/cart_detail.html', context)


@ssl_required
@login_required
def remove_from_cart(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
    cart_item.delete()
    return redirect('cart:view_cart')


@ssl_required
@login_required
def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        try:
            quantity = int(quantity)
            if quantity > 0:
                cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
                cart_item.quantity = quantity
                cart_item.save()
            elif quantity == 0: # Remover se a quantidade for 0
                cart_item = get_object_or_404(CartItem, id=cart_item_id, cart__user=request.user)
                cart_item.delete()
        except (ValueError, TypeError):
            pass # Lidar com erro de quantidade inválida
    return redirect('cart:view_cart')
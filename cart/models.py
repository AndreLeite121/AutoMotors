# cart/models.py
from django.db import models
from django.conf import settings
from garagem.models import Veiculo
from acessorios.models import Acessorio

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrinho de {self.user.username if self.user.username else self.user.email}"

    def get_total_price(self):
        total = 0
        for item in self.items.all():
            total += item.get_total_item_price()
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    # Para permitir tanto produtos do cardápio quanto itens de office no mesmo carrinho
    # Um deles será preenchido, o outro será None.
    veiculo_item = models.ForeignKey(Veiculo, on_delete=models.CASCADE, null=True, blank=True)
    acessorio_item = models.ForeignKey(Acessorio, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    # Preço no momento da adição, para evitar problemas se o preço do produto mudar
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                name="%(app_label)s_%(class)s_either_veiculo_or_acessorio_item",
                check=(
                    models.Q(veiculo_item__isnull=False, acessorio_item__isnull=True) |
                    models.Q(veiculo_item__isnull=True, acessorio_item__isnull=False)
                ),
            )
        ]

    def __str__(self):
        if self.veiculo_item:
            return f"{self.quantity} x {self.veiculo_item.nome} no carrinho de {self.cart.user.username if self.cart.user.username else self.cart.user.email}"
        elif self.acessorio_item:
            return f"{self.quantity} x {self.acessorio_item.nome} no carrinho de {self.cart.user.username if self.cart.user.username else self.cart.user.email}"
        return "Item inválido no carrinho"

    @property
    def item_object(self):
        return self.veiculo_item if self.veiculo_item else self.acessorio_item

    def get_item_price(self):
        if self.price_at_purchase is not None:
            return self.price_at_purchase
        return self.item_object.preco if self.item_object else 0

    def get_total_item_price(self):
        return self.quantity * self.get_item_price()
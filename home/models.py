# home/models.py — AutoMotors
from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver


class Review(models.Model):
    """Avaliação pública da loja."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Avaliação de {self.user.username} - {self.rating} estrelas"

    class Meta:
        ordering = ["-created_at"]


class UserProfile(models.Model):
    """Dados pessoais do cliente AutoMotors.

    Os campos sensíveis (CPF, telefone, endereço) só devem ser acessados em
    rotas HTTPS — o decorator `home.decorators.ssl_required` cuida disso.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    # Contato
    telefone = models.CharField(max_length=20, blank=True, default="",
                                help_text="Ex: (38) 99999-9999")

    # Endereço
    cep = models.CharField(max_length=10, blank=True, default="")
    endereco = models.CharField(max_length=200, blank=True, default="")
    numero = models.CharField(max_length=20, blank=True, default="")
    complemento = models.CharField(max_length=100, blank=True, default="")
    cidade = models.CharField(max_length=100, blank=True, default="")
    estado = models.CharField(max_length=2, blank=True, default="")

    # Documento (sensível, opcional)
    cpf = models.CharField(max_length=14, blank=True, default="",
                           help_text="Somente para emissão de nota fiscal.")

    aceita_marketing = models.BooleanField(
        default=False,
        help_text="Receber ofertas e novidades por e-mail.",
    )

    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def criar_perfil_automaticamente(sender, instance, created, **kwargs):
    """Cria UserProfile no momento em que um User é criado."""
    if created:
        UserProfile.objects.get_or_create(user=instance)


class HistoricoInteresse(models.Model):
    """Registra todo carro que entrou na lista de interesse de um usuário.

    Diferente de `cart.CartItem`, este registro é PERMANENTE — não é apagado
    quando o usuário remove o carro de `/interesse/`. Serve como histórico de
    intenção de compra do cliente.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="historico_interesses",
    )
    veiculo_item = models.ForeignKey(
        "garagem.Veiculo",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="historicos",
    )

    # Snapshot para o caso de o veículo ser removido do estoque
    nome_snapshot = models.CharField(max_length=200, blank=True, default="")
    preco_snapshot = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    foto_snapshot = models.CharField(max_length=300, blank=True, default="")

    primeira_marcacao = models.DateTimeField(auto_now_add=True)
    ultima_marcacao = models.DateTimeField(auto_now=True)
    vezes_marcado = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["-ultima_marcacao"]
        unique_together = [("user", "veiculo_item")]

    def __str__(self):
        return f"{self.user} demonstrou interesse em {self.nome_snapshot}"

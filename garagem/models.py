from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date


class Veiculo(models.Model):
    """
    Modelo de veículo do estoque AutoMotors.
    Representa um carro seminovo disponível para venda.
    """

    CATEGORIAS = (
        ("ALL", "Todos"),
        ("SUV", "SUV"),
        ("SED", "Sedan"),
        ("HAT", "Hatch"),
        ("PIC", "Picape"),
        ("UTI", "Utilitário"),
        ("ESP", "Esportivo"),
    )

    COMBUSTIVEIS = (
        ("FLEX", "Flex"),
        ("GAS",  "Gasolina"),
        ("DIE",  "Diesel"),
        ("HIB",  "Híbrido"),
        ("ELE",  "Elétrico"),
        ("GNV",  "GNV"),
    )

    CAMBIOS = (
        ("MAN", "Manual"),
        ("AUT", "Automático"),
        ("CVT", "CVT"),
        ("AUM", "Automatizado"),
    )

    PROMOCAO = (
        ("S", "Sim"),
        ("N", "Não"),
    )

    # Identificação
    nome = models.CharField(max_length=200, help_text="Ex: Honda Civic EXL 2.0")
    marca = models.CharField(max_length=80, blank=True, default="")
    modelo = models.CharField(max_length=120, blank=True, default="")

    # Categoria (mantém o campo 'tipo' usado pelo template legado)
    tipo = models.CharField(max_length=50, choices=CATEGORIAS, default="ALL")

    # Especificações
    ano_fabricacao = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1950), MaxValueValidator(date.today().year + 1)],
    )
    ano_modelo = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1950), MaxValueValidator(date.today().year + 2)],
    )
    quilometragem = models.PositiveIntegerField(
        null=True, blank=True, help_text="KM rodados"
    )
    combustivel = models.CharField(max_length=4, choices=COMBUSTIVEIS, default="FLEX")
    cambio = models.CharField(max_length=3, choices=CAMBIOS, default="AUT")
    cor = models.CharField(max_length=40, blank=True, default="")

    # Comercial
    promocao = models.CharField(max_length=50, choices=PROMOCAO, default="N")
    preco = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Conteúdo de página
    descricao = models.TextField(blank=True, null=True)
    foto = models.ImageField(
        upload_to='fotos_veiculos/',
        default="fotos_veiculos/default.png",
        blank=True, null=True,
    )

    adicionado = models.DateTimeField(auto_now_add=True)
    editado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-adicionado"]

    def __str__(self):
        return self.nome

    @property
    def titulo(self):
        return f"{self.marca} {self.modelo}".strip() or self.nome

    @property
    def foto_principal(self):
        """Retorna a primeira foto da galeria; cai para `foto` se vazio."""
        principal = self.fotos.filter(principal=True).first()
        if principal:
            return principal.imagem
        primeira = self.fotos.order_by("ordem").first()
        if primeira:
            return primeira.imagem
        return self.foto


class VeiculoFoto(models.Model):
    """Foto adicional de um veículo (galeria)."""

    veiculo = models.ForeignKey(
        Veiculo,
        on_delete=models.CASCADE,
        related_name="fotos",
    )
    imagem = models.ImageField(upload_to="fotos_veiculos_galeria/")
    ordem = models.PositiveIntegerField(default=0)
    principal = models.BooleanField(default=False)
    adicionado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["veiculo_id", "ordem"]

    def __str__(self):
        return f"Foto {self.ordem} de {self.veiculo.nome}"

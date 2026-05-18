from django.contrib import admin
from django.utils.html import format_html

from .models import Veiculo, VeiculoFoto


class VeiculoFotoInline(admin.TabularInline):
    model = VeiculoFoto
    extra = 1
    fields = ("preview", "imagem", "ordem", "principal")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj and obj.imagem:
            return format_html(
                '<img src="{}" style="height: 60px; border-radius: 4px;">',
                obj.imagem.url,
            )
        return "—"


@admin.register(Veiculo)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        "thumb", "nome", "marca", "ano_modelo",
        "quilometragem", "preco", "tipo", "promocao", "total_fotos",
    )
    list_display_links = ("nome",)
    list_filter = ("tipo", "combustivel", "cambio", "promocao", "marca")
    search_fields = ("nome", "marca", "modelo", "cor")
    readonly_fields = ("adicionado", "editado")
    inlines = [VeiculoFotoInline]
    fieldsets = (
        ("Identificação", {
            "fields": ("nome", "marca", "modelo", "tipo", "cor"),
        }),
        ("Especificações", {
            "fields": ("ano_fabricacao", "ano_modelo", "quilometragem", "combustivel", "cambio"),
        }),
        ("Comercial", {
            "fields": ("preco", "promocao"),
        }),
        ("Conteúdo", {
            "fields": ("descricao", "foto"),
            "description": "A foto principal abaixo é usada como fallback. Para galeria, "
                           "adicione fotos na seção 'Fotos do Veículo' abaixo.",
        }),
        ("Metadados", {
            "fields": ("adicionado", "editado"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="")
    def thumb(self, obj):
        url = obj.foto_principal.url if obj.foto_principal else None
        if url:
            return format_html(
                '<img src="{}" style="height: 40px; width: 60px; object-fit: cover; border-radius: 3px;">',
                url,
            )
        return "—"

    @admin.display(description="Fotos")
    def total_fotos(self, obj):
        return obj.fotos.count()


@admin.register(VeiculoFoto)
class VeiculoFotoAdmin(admin.ModelAdmin):
    list_display = ("veiculo", "ordem", "principal", "thumb")
    list_filter = ("principal", "veiculo")
    search_fields = ("veiculo__nome",)

    @admin.display(description="Preview")
    def thumb(self, obj):
        if obj.imagem:
            return format_html(
                '<img src="{}" style="height: 50px; border-radius: 4px;">',
                obj.imagem.url,
            )
        return "—"

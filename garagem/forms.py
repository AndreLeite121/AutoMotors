from django import forms
from .models import Veiculo


class CarForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = [
            "nome", "marca", "modelo", "tipo",
            "ano_fabricacao", "ano_modelo", "quilometragem",
            "combustivel", "cambio", "cor",
            "preco", "promocao",
            "descricao", "foto",
        ]
        widgets = {
            "nome":            forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Honda Civic EXL 2.0"}),
            "marca":           forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Honda"}),
            "modelo":          forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Civic EXL"}),
            "tipo":            forms.Select(attrs={"class": "form-select"}),
            "ano_fabricacao":  forms.NumberInput(attrs={"class": "form-control", "placeholder": "2020"}),
            "ano_modelo":      forms.NumberInput(attrs={"class": "form-control", "placeholder": "2021"}),
            "quilometragem":   forms.NumberInput(attrs={"class": "form-control", "placeholder": "KM rodados"}),
            "combustivel":     forms.Select(attrs={"class": "form-select"}),
            "cambio":          forms.Select(attrs={"class": "form-select"}),
            "cor":             forms.TextInput(attrs={"class": "form-control", "placeholder": "Ex: Preto Pérola"}),
            "preco":           forms.NumberInput(attrs={"class": "form-control", "placeholder": "R$"}),
            "promocao":        forms.Select(attrs={"class": "form-select"}),
            "descricao":       forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Descrição do veículo, itens de série, opcionais..."}),
        }

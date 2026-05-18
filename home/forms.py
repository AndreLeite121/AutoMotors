# home/forms.py — AutoMotors
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, UserProfile


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "form-control")
            if name == "username":
                field.widget.attrs.setdefault("placeholder", "Escolha um nome de usuário")
            if name == "email":
                field.widget.attrs.setdefault("placeholder", "voce@exemplo.com")
                field.required = True


class UserBasicsForm(forms.ModelForm):
    """Campos do User nativo do Django (email, nome) editáveis pelo cliente."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome"}),
            "last_name":  forms.TextInput(attrs={"class": "form-control", "placeholder": "Sobrenome"}),
            "email":      forms.EmailInput(attrs={"class": "form-control", "placeholder": "voce@exemplo.com"}),
        }
        labels = {
            "first_name": "Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }


class UserProfileForm(forms.ModelForm):
    """Dados sensíveis — só editados em rota HTTPS."""

    class Meta:
        model = UserProfile
        fields = (
            "telefone", "cpf",
            "cep", "endereco", "numero", "complemento", "cidade", "estado",
            "aceita_marketing",
        )
        widgets = {
            "telefone":    forms.TextInput(attrs={"class": "form-control", "placeholder": "(38) 99999-9999"}),
            "cpf":         forms.TextInput(attrs={"class": "form-control", "placeholder": "000.000.000-00"}),
            "cep":         forms.TextInput(attrs={"class": "form-control", "placeholder": "00000-000"}),
            "endereco":    forms.TextInput(attrs={"class": "form-control", "placeholder": "Rua / Avenida"}),
            "numero":      forms.TextInput(attrs={"class": "form-control", "placeholder": "Nº"}),
            "complemento": forms.TextInput(attrs={"class": "form-control", "placeholder": "Apto, bloco, ponto de referência"}),
            "cidade":      forms.TextInput(attrs={"class": "form-control", "placeholder": "Cidade"}),
            "estado":      forms.TextInput(attrs={"class": "form-control", "placeholder": "UF", "maxlength": "2"}),
            "aceita_marketing": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
        labels = {
            "telefone":         "Telefone",
            "cpf":              "CPF",
            "cep":              "CEP",
            "endereco":         "Endereço",
            "numero":           "Número",
            "complemento":      "Complemento",
            "cidade":           "Cidade",
            "estado":           "Estado",
            "aceita_marketing": "Quero receber ofertas e novidades por e-mail.",
        }


class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        min_value=0,
        max_value=5,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Deixe seu comentário aqui...",
            }),
        }
        labels = {
            "comment": "Comentário",
        }

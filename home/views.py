from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Review, UserProfile, HistoricoInteresse
from .forms import ReviewForm, CustomUserCreationForm, UserProfileForm, UserBasicsForm
from .decorators import ssl_required, http_only


@http_only
def index(request):
    """Landing AutoMotors (HTTP puro — página social)."""
    return render(request, "index.html", {
        "reviews": Review.objects.all()[:6],
        "review_form": ReviewForm(),
    })


@login_required
def add_review(request):
    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            messages.success(request, "Obrigado pela sua avaliação!")
        else:
            for _, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    return redirect("garagem:index")


@ssl_required
def signup_view(request):
    """Cadastro de novo cliente (HTTPS — coleta email + senha)."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Conta criada com sucesso! Complete seu perfil.")
            return redirect("home:perfil")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


@ssl_required
@login_required
def perfil_view(request):
    """Página de perfil — HTTPS obrigatório (CPF, endereço, telefone)."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        basics_form = UserBasicsForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        if basics_form.is_valid() and profile_form.is_valid():
            basics_form.save()
            profile_form.save()
            messages.success(request, "Perfil atualizado com sucesso.")
            return redirect("home:perfil")
        messages.error(request, "Há erros no formulário. Confira os campos destacados.")
    else:
        basics_form = UserBasicsForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)

    return render(request, "home/perfil.html", {
        "basics_form": basics_form,
        "profile_form": profile_form,
        "profile": profile,
    })


@ssl_required
@login_required
def meu_historico_view(request):
    """Histórico de interesses — HTTPS (lista privada do usuário)."""
    historicos = (
        HistoricoInteresse.objects
        .filter(user=request.user)
        .select_related("veiculo_item")
        .order_by("-ultima_marcacao")
    )
    return render(request, "home/meu_historico.html", {
        "historicos": historicos,
    })

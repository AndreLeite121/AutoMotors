from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from home.decorators import http_only
from home.models import Review
from home.forms import ReviewForm
from .forms import CarForm
from .models import Veiculo


@http_only
def index(request):
    """Catálogo principal da garagem AutoMotors (HTTP — público)."""
    cat = request.GET.get("cat")
    qs = Veiculo.objects.all()
    if cat:
        qs = qs.filter(tipo=cat.upper())

    return render(request, "all.html", {
        "lista": qs,
        "reviews": Review.objects.all().order_by("-created_at")[:6],
        "review_form": ReviewForm(),
        "categoria_atual": cat,
    })


@http_only
def indexall(request):
    """Alias legado para /garagem/all/."""
    return index(request)


def adc(request):
    """Cadastro de veículo (área interna)."""
    form = CarForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("garagem:index")
    return render(request, "adc_car.html", {"form": form})


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


@http_only
def detalhes(request, pk):
    """Página de detalhe do carro (HTTP — público)."""
    car = get_object_or_404(Veiculo, pk=pk)
    return render(request, "detalhes.html", {"car": car})

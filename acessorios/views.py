# acessorios/views.py
from django.shortcuts import render
from home.decorators import http_only
from .models import Acessorio


@http_only
def office_list(request):
    """Acessórios e serviços (HTTP — catálogo público)."""
    items = Acessorio.objects.filter(disponivel=True)
    return render(request, 'acessorios/office_list.html', {'acessorios': items})

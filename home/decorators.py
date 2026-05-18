"""Decorators de proteção HTTP/HTTPS — AutoMotors.

O TPIII_SASI exige que páginas com dados sensíveis (login, perfil, checkout,
admin) sejam servidas por HTTPS e que páginas públicas permaneçam em HTTP
puro, sob pena de perder 60% da nota se a segurança for global.

Estratégia: dois processos Django paralelos.
    HTTP  → manage.py runserver       127.0.0.1:8000
    HTTPS → manage.py runsslserver    127.0.0.1:8443

Quando o usuário acessa uma rota sensível por HTTP, `ssl_required` faz um
HTTP 301 para o mesmo path no host HTTPS. O inverso ocorre com `http_only`.
"""

from functools import wraps

from django.conf import settings
from django.http import HttpResponseRedirect


def _redirect_to(host: str, request) -> HttpResponseRedirect:
    """Constrói o redirect preservando path + query string do usuário."""
    return HttpResponseRedirect(host + request.get_full_path())


def ssl_required(view_func):
    """Garante que a view só seja servida em HTTPS.

    Se o request chega via HTTP, redireciona para o mesmo path no host HTTPS.
    Quando AUTOMOTORS_HTTPS_HOST estiver vazio (dev sem certs), apenas repassa.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        https_host = getattr(settings, 'AUTOMOTORS_HTTPS_HOST', '')
        if request.is_secure() or not https_host:
            return view_func(request, *args, **kwargs)
        return _redirect_to(f'https://{https_host}', request)

    return _wrapped


def http_only(view_func):
    """Devolve a navegação pública para HTTP puro (economia + atende exigência TPIII).

    Se o usuário caiu em HTTPS numa página pública (clicou num link absoluto,
    por exemplo), volta para HTTP. Em produção real isso não faria sentido,
    mas para o trabalho acadêmico cumpre a regra do enunciado de NÃO ter
    HTTPS global no sistema inteiro.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        http_host = getattr(settings, 'AUTOMOTORS_HTTP_HOST', '')
        if not request.is_secure() or not http_host:
            return view_func(request, *args, **kwargs)
        return _redirect_to(f'http://{http_host}', request)

    return _wrapped

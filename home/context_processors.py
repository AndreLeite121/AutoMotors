"""Context processors AutoMotors.

Expõe AUTOMOTORS_HTTP_HOST e AUTOMOTORS_HTTPS_HOST em todos os templates,
permitindo gerar links absolutos que pulam entre os dois protocolos —
necessário para implementar HTTPS seletivo no TPIII_SASI.

Uso nos templates:
    <a href="{{ HTTPS_BASE }}{% url 'login' %}">Entrar</a>
    <a href="{{ HTTP_BASE  }}{% url 'home:index' %}">Voltar para a home</a>
"""

from django.conf import settings


def protocolo_hosts(request):
    https_host = getattr(settings, 'AUTOMOTORS_HTTPS_HOST', '')
    http_host  = getattr(settings, 'AUTOMOTORS_HTTP_HOST', '')
    return {
        'HTTP_BASE':  f'http://{http_host}'   if http_host  else '',
        'HTTPS_BASE': f'https://{https_host}' if https_host else '',
        'IS_SECURE':  request.is_secure(),
    }

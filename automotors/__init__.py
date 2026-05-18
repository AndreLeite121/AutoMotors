"""AutoMotors — Django project init.

Aplica o patch de compatibilidade de SSL antes de qualquer outra coisa,
para o django-sslserver funcionar no Python 3.12+.
"""
from . import _ssl_compat  # noqa: F401

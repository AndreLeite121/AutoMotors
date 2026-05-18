"""Patch de compatibilidade — django-sslserver no Python 3.12+.

`ssl.wrap_socket()` foi marcado como deprecated em Python 3.6 e removido em
Python 3.12. Como o django-sslserver (0.22, sem manutenção desde 2018) ainda
usa essa API antiga, criamos aqui um shim que delega para o `SSLContext`
moderno — mantendo o comportamento esperado pelo runsslserver.

Este módulo é importado por automotors/__init__.py antes de qualquer outro
código Django, garantindo que o patch esteja ativo quando o sslserver for
carregado.
"""

import ssl

if not hasattr(ssl, "wrap_socket"):

    def _wrap_socket_compat(
        sock,
        keyfile=None,
        certfile=None,
        server_side=False,
        cert_reqs=ssl.CERT_NONE,
        ssl_version=None,
        ca_certs=None,
        do_handshake_on_connect=True,
        suppress_ragged_eofs=True,
        ciphers=None,
    ):
        """Substituto moderno de ssl.wrap_socket() usando SSLContext."""
        protocol = ssl.PROTOCOL_TLS_SERVER if server_side else ssl.PROTOCOL_TLS_CLIENT
        context = ssl.SSLContext(protocol)
        if certfile:
            context.load_cert_chain(certfile=certfile, keyfile=keyfile)
        if ca_certs:
            context.load_verify_locations(cafile=ca_certs)
        if cert_reqs is not None:
            context.verify_mode = cert_reqs
        if ciphers:
            context.set_ciphers(ciphers)

        return context.wrap_socket(
            sock,
            server_side=server_side,
            do_handshake_on_connect=do_handshake_on_connect,
            suppress_ragged_eofs=suppress_ragged_eofs,
        )

    ssl.wrap_socket = _wrap_socket_compat

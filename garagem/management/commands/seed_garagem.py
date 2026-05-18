"""Popula a garagem AutoMotors com carros de exemplo.

Uso:
    python manage.py seed_garagem            # limpa e repopula
    python manage.py seed_garagem --keep     # só adiciona, sem limpar
"""

from __future__ import annotations

import shutil
import ssl
import urllib.request
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from garagem.models import Veiculo
from acessorios.models import Acessorio


# Fotos do Unsplash (CC0). Nomes do arquivo correspondem ao slug do carro.
CARROS = [
    {
        "slug": "civic-exl-2021",
        "nome": "Honda Civic EXL 2.0",
        "marca": "Honda", "modelo": "Civic EXL",
        "tipo": "SED",
        "ano_fabricacao": 2020, "ano_modelo": 2021,
        "quilometragem": 38900, "combustivel": "FLEX", "cambio": "CVT",
        "cor": "Preto Pérola",
        "preco": Decimal("119900.00"), "promocao": "N",
        "descricao": "Sedan premium com bancos de couro, central multimídia 7\", "
                     "câmera de ré e único dono. Revisões em concessionária.",
        "foto_url": "https://images.unsplash.com/photo-1542362567-b07e54358753?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "corolla-xei-2022",
        "nome": "Toyota Corolla XEi 2.0",
        "marca": "Toyota", "modelo": "Corolla XEi",
        "tipo": "SED",
        "ano_fabricacao": 2021, "ano_modelo": 2022,
        "quilometragem": 24500, "combustivel": "FLEX", "cambio": "CVT",
        "cor": "Prata Metálico",
        "preco": Decimal("139800.00"), "promocao": "S",
        "descricao": "Sedan top de linha com Toyota Safety Sense, sete airbags, "
                     "controle de cruzeiro adaptativo e teto solar.",
        "foto_url": "https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "hb20-comfort-2020",
        "nome": "Hyundai HB20 Comfort Plus",
        "marca": "Hyundai", "modelo": "HB20 1.0 Comfort",
        "tipo": "HAT",
        "ano_fabricacao": 2019, "ano_modelo": 2020,
        "quilometragem": 52300, "combustivel": "FLEX", "cambio": "MAN",
        "cor": "Branco Polar",
        "preco": Decimal("58900.00"), "promocao": "N",
        "descricao": "Hatch econômico, ar-condicionado, direção elétrica e "
                     "central multimídia com Android Auto.",
        "foto_url": "https://images.unsplash.com/photo-1547245324-d777c6f05e80?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "golf-gti-2019",
        "nome": "Volkswagen Golf GTI",
        "marca": "Volkswagen", "modelo": "Golf GTI 2.0 TSI",
        "tipo": "ESP",
        "ano_fabricacao": 2018, "ano_modelo": 2019,
        "quilometragem": 41200, "combustivel": "GAS", "cambio": "AUT",
        "cor": "Vermelho Tornado",
        "preco": Decimal("159500.00"), "promocao": "N",
        "descricao": "Hot hatch icônico, 220cv, câmbio DSG de 6 marchas, "
                     "rodas 18\" e bancos esportivos.",
        "foto_url": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "compass-longitude-2022",
        "nome": "Jeep Compass Longitude T270",
        "marca": "Jeep", "modelo": "Compass Longitude 1.3 Turbo",
        "tipo": "SUV",
        "ano_fabricacao": 2021, "ano_modelo": 2022,
        "quilometragem": 31700, "combustivel": "FLEX", "cambio": "AUT",
        "cor": "Cinza Granito",
        "preco": Decimal("184900.00"), "promocao": "S",
        "descricao": "SUV familiar com sensor de estacionamento, painel digital, "
                     "porta-malas de 410L e garantia de fábrica vigente.",
        "foto_url": "https://images.unsplash.com/photo-1606664515524-ed2f786a0bd6?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "hilux-srx-2021",
        "nome": "Toyota Hilux SRX 4x4",
        "marca": "Toyota", "modelo": "Hilux SRX 2.8 Diesel 4x4",
        "tipo": "PIC",
        "ano_fabricacao": 2020, "ano_modelo": 2021,
        "quilometragem": 67400, "combustivel": "DIE", "cambio": "AUT",
        "cor": "Branco Diamante",
        "preco": Decimal("249000.00"), "promocao": "N",
        "descricao": "Picape diesel 4x4, capota marítima, santantônio, "
                     "engate de reboque e câmera 360°.",
        "foto_url": "https://images.unsplash.com/photo-1605559424843-9e4c228bf1c2?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "bmw-320i-2020",
        "nome": "BMW 320i M Sport",
        "marca": "BMW", "modelo": "320i M Sport 2.0 Turbo",
        "tipo": "ESP",
        "ano_fabricacao": 2019, "ano_modelo": 2020,
        "quilometragem": 47800, "combustivel": "GAS", "cambio": "AUT",
        "cor": "Preto Safira",
        "preco": Decimal("214900.00"), "promocao": "N",
        "descricao": "Sedan premium alemão com pacote M Sport, head-up display, "
                     "bancos elétricos com memória e som Harman Kardon.",
        "foto_url": "https://images.unsplash.com/photo-1555215695-3004980ad54e?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "kwid-zen-2023",
        "nome": "Renault Kwid Zen 1.0",
        "marca": "Renault", "modelo": "Kwid Zen 1.0",
        "tipo": "HAT",
        "ano_fabricacao": 2022, "ano_modelo": 2023,
        "quilometragem": 18900, "combustivel": "FLEX", "cambio": "MAN",
        "cor": "Laranja Ocre",
        "preco": Decimal("64500.00"), "promocao": "S",
        "descricao": "Hatch compacto urbano, baixo consumo, central multimídia "
                     "com espelhamento e airbags duplos.",
        "foto_url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=1200&q=80&fm=jpg",
    },
    {
        "slug": "fiat-toro-volcano-2022",
        "nome": "Fiat Toro Volcano 2.0 Diesel",
        "marca": "Fiat", "modelo": "Toro Volcano 2.0 Diesel 4x4",
        "tipo": "PIC",
        "ano_fabricacao": 2021, "ano_modelo": 2022,
        "quilometragem": 43200, "combustivel": "DIE", "cambio": "AUT",
        "cor": "Vermelho Marsala",
        "preco": Decimal("174900.00"), "promocao": "N",
        "descricao": "Picape média 4x4 com tração nas quatro rodas, capota rígida, "
                     "bancos de couro e teto solar.",
        "foto_url": "https://images.unsplash.com/photo-1568844293986-8d0400bd4745?w=1200&q=80&fm=jpg",
    },
]

ACESSORIOS = [
    {
        "nome": "Tapete de borracha automotivo (jogo)",
        "descricao": "Conjunto com 4 tapetes de borracha resistente, sob medida para "
                     "sedans e SUVs. Antiderrapante e impermeável.",
        "preco": Decimal("189.90"), "tipo_item": "PROD",
    },
    {
        "nome": "Higienização interna completa",
        "descricao": "Serviço completo de limpeza interna: bancos, painel, teto, "
                     "porta-malas, com aspersão e remoção de odores.",
        "preco": Decimal("259.00"), "tipo_item": "SERV",
    },
    {
        "nome": "Película de proteção solar (jogo)",
        "descricao": "Instalação de película G20 nos 5 vidros do veículo, com "
                     "garantia de 5 anos contra descolamento e bolhas.",
        "preco": Decimal("420.00"), "tipo_item": "SERV",
    },
]


class Command(BaseCommand):
    help = "Popula a garagem AutoMotors com carros e acessórios de exemplo."

    def add_arguments(self, parser):
        parser.add_argument("--keep", action="store_true",
                            help="Não apaga registros existentes antes de popular.")
        parser.add_argument("--no-photos", action="store_true",
                            help="Não baixa fotos do Unsplash (usa foto default).")

    def handle(self, *args, **options):
        keep = options.get("keep")
        no_photos = options.get("no_photos")

        if not keep:
            removidos_cars = Veiculo.objects.all().count()
            removidos_off = Acessorio.objects.all().count()
            Veiculo.objects.all().delete()
            Acessorio.objects.all().delete()
            self.stdout.write(self.style.WARNING(
                f"Removidos: {removidos_cars} carros e {removidos_off} acessórios antigos."
            ))

            # Limpa fotos antigas do diretório media (mantém default.png)
            media_dir = Path(settings.MEDIA_ROOT) / "fotos_veiculos"
            if media_dir.exists():
                for f in media_dir.iterdir():
                    if f.is_file() and f.name != "default.png":
                        f.unlink()
                self.stdout.write(self.style.WARNING(
                    f"Fotos antigas removidas de {media_dir} (default.png preservado)."
                ))

        self.stdout.write(self.style.MIGRATE_HEADING("Criando carros..."))
        for data in CARROS:
            self._criar_carro(data, no_photos=no_photos)

        self.stdout.write(self.style.MIGRATE_HEADING("Criando acessórios..."))
        for data in ACESSORIOS:
            Acessorio.objects.create(**data)
            self.stdout.write(f"  · {data['nome']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nGaragem populada: {Veiculo.objects.count()} carros + "
            f"{Acessorio.objects.count()} acessórios."
        ))

    def _criar_carro(self, data, no_photos=False):
        foto_url = data.pop("foto_url", None)
        slug = data.pop("slug")
        carro = Veiculo.objects.create(**data)

        if no_photos or not foto_url:
            self.stdout.write(f"  · {carro.nome} (sem foto)")
            return

        try:
            ctx = ssl.create_default_context()
            req = urllib.request.Request(foto_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                content = resp.read()
            filename = f"{slug}.jpg"
            carro.foto.save(filename, ContentFile(content), save=True)
            self.stdout.write(f"  · {carro.nome}  ({len(content) // 1024} kB)")
        except Exception as exc:
            self.stdout.write(self.style.WARNING(
                f"  · {carro.nome}  (foto falhou: {exc} — usando default)"
            ))

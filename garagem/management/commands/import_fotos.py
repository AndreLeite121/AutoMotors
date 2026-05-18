"""Importa fotos dos carros a partir de um diretório com subpastas por carro.

Estrutura esperada (pasta `Carros/` versionada na raiz do projeto):
    Carros/
        Honda Civic EXL 2.0/
            foto1.png
            foto2.png
            ...
        BMW 320i M Sport/
            ...

Uso:
    python manage.py import_fotos                 # usa Carros/ relativo à raiz
    python manage.py import_fotos /outro/caminho  # caminho customizado
    python manage.py import_fotos --clear         # apaga galeria antes
"""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from garagem.models import Veiculo, VeiculoFoto


# Mapeamento explícito: pasta no disco → nome exato (ou substring) no Veiculo.nome
MAPA_PASTAS = {
    "BMW 320i M Sport":           "BMW 320i M Sport",
    "Fiat toro 21:22":            "Fiat Toro",
    "Honda Civic EXL 2.0":        "Honda Civic",
    "Hyundai HB20 Comfort Plus":  "Hyundai HB20",
    "Jeep Compass Longitude T270":"Jeep Compass",
    "renault kwid zen 1.0":       "Renault Kwid",
    "Toyota Corolla XEi 2.0":     "Toyota Corolla",
    "Toyota Hilux SRX 4x4":       "Toyota Hilux",
    "Volkswagen Golf GTI":        "Volkswagen Golf",
}

EXTENSOES = {".png", ".jpg", ".jpeg", ".webp", ".avif"}


class Command(BaseCommand):
    help = "Importa fotos dos carros de um diretório local para a galeria."

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            nargs="?",
            default=str(Path(settings.BASE_DIR) / "Carros"),
            help="Caminho raiz com as subpastas de cada carro "
                 "(padrão: Carros/ na raiz do projeto).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Apaga toda a galeria antes de importar.",
        )

    def handle(self, *args, **options):
        root = Path(options["source"]).expanduser()
        if not root.exists():
            raise CommandError(f"Diretório não existe: {root}")

        if options["clear"]:
            n = VeiculoFoto.objects.count()
            VeiculoFoto.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Galeria limpa: {n} fotos removidas."))

        total = 0
        for pasta_nome, busca in MAPA_PASTAS.items():
            pasta = root / pasta_nome
            if not pasta.exists():
                self.stdout.write(self.style.WARNING(f"⚠️  Pasta ausente: {pasta_nome}"))
                continue

            carro = Veiculo.objects.filter(nome__icontains=busca).first()
            if not carro:
                self.stdout.write(self.style.WARNING(
                    f"⚠️  Não achei carro para a pasta '{pasta_nome}' (busca: {busca})"
                ))
                continue

            arquivos = sorted(
                (f for f in pasta.iterdir() if f.is_file() and f.suffix.lower() in EXTENSOES),
                key=lambda f: f.name,
            )
            if not arquivos:
                self.stdout.write(self.style.WARNING(f"⚠️  {pasta_nome}: sem fotos suportadas"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(
                f"\n→ {carro.nome}  ({len(arquivos)} foto{'s' if len(arquivos)>1 else ''})"
            ))

            # Limpa fotos antigas DESSE carro pra não duplicar
            carro.fotos.all().delete()

            for idx, arq in enumerate(arquivos):
                with arq.open("rb") as fh:
                    nova_foto = VeiculoFoto(
                        veiculo=carro,
                        ordem=idx,
                        principal=(idx == 0),
                    )
                    nova_foto.imagem.save(arq.name, File(fh), save=True)
                self.stdout.write(f"   · {arq.name}  ({arq.stat().st_size // 1024} kB)")
                total += 1

            # Atualiza a foto principal (campo Veiculo.foto)
            primeira = carro.fotos.order_by("ordem").first()
            if primeira:
                carro.foto = primeira.imagem
                carro.save(update_fields=["foto"])

        self.stdout.write(self.style.SUCCESS(f"\nImportadas {total} fotos no total."))

from django.db import migrations, models


class Migration(migrations.Migration):
    """Renomeia Cardapio→Veiculo e CardapioFoto→VeiculoFoto."""

    dependencies = [
        ("garagem", "0010_cardapiofoto"),
    ]

    operations = [
        migrations.RenameModel(old_name="Cardapio", new_name="Veiculo"),
        migrations.RenameModel(old_name="CardapioFoto", new_name="VeiculoFoto"),
        migrations.RenameField(
            model_name="veiculofoto",
            old_name="cardapio",
            new_name="veiculo",
        ),
        migrations.AlterModelOptions(
            name="veiculofoto",
            options={"ordering": ["veiculo_id", "ordem"]},
        ),
        migrations.AlterField(
            model_name="veiculo",
            name="foto",
            field=models.ImageField(
                blank=True,
                default="fotos_veiculos/default.png",
                null=True,
                upload_to="fotos_veiculos/",
            ),
        ),
        migrations.AlterField(
            model_name="veiculofoto",
            name="imagem",
            field=models.ImageField(upload_to="fotos_veiculos_galeria/"),
        ),
    ]

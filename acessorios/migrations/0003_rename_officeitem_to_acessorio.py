from django.db import migrations


class Migration(migrations.Migration):
    """Renomeia OfficeItem→Acessorio."""

    dependencies = [
        ("acessorios", "0002_officeitem_delete_op"),
    ]

    operations = [
        migrations.RenameModel(old_name="OfficeItem", new_name="Acessorio"),
    ]

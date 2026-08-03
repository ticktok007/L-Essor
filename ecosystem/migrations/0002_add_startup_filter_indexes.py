# ecosystem/migrations/0002_add_startup_filter_indexes.py
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ecosystem", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="startup",
            name="funding_stage",
            field=models.CharField(blank=True, max_length=24),
        ),
        migrations.AddIndex(
            model_name="startup",
            index=models.Index(
                fields=["funding_stage"],
                name="ecosystem_startup_funding_stage_btree_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="startup",
            index=models.Index(
                fields=["sector"],
                name="ecosystem_startup_sector_btree_idx",
            ),
        ),
    ]

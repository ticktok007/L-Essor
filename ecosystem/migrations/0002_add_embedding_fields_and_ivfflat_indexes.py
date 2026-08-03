from django.db import migrations
from pgvector.django import VectorField


def create_ivfflat_indexes(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_startup_pitch_ivfflat ON ecosystem_startup USING ivfflat (pitch_embedding vector_cosine_ops) WITH (lists = 100);"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_investor_mandate_ivfflat ON ecosystem_investor USING ivfflat (mandate_embedding vector_cosine_ops) WITH (lists = 100);"
            )


def drop_ivfflat_indexes(apps, schema_editor):
    if schema_editor.connection.vendor == "postgresql":
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("DROP INDEX IF EXISTS idx_startup_pitch_ivfflat;")
            cursor.execute("DROP INDEX IF EXISTS idx_investor_mandate_ivfflat;")


class Migration(migrations.Migration):
    dependencies = [("ecosystem", "0001_initial")]
    operations = [
        migrations.AddField(
            model_name="startup",
            name="pitch_embedding",
            field=VectorField(dimensions=384, null=True, blank=True),
        ),
        migrations.AddField(
            model_name="investor",
            name="mandate_embedding",
            field=VectorField(dimensions=384, null=True, blank=True),
        ),
        migrations.RunPython(create_ivfflat_indexes, reverse_code=drop_ivfflat_indexes),
    ]


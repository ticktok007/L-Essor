# ecosystem/migrations/00XX_add_embedding_fields_and_ivfflat_indexes.py
from django.db import migrations
import pgvector.django


class Migration(migrations.Migration):

    dependencies = [
        ('ecosystem', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='startup',
            name='pitch_embedding',
            field=pgvector.django.VectorField(dimensions=384, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='investor',
            name='mandate_embedding',
            field=pgvector.django.VectorField(dimensions=384, null=True, blank=True),
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX startup_pitch_ivfflat_idx
            ON ecosystem_startup
            USING ivfflat (pitch_embedding vector_cosine_ops)
            WITH (lists = 100);
            """,
            reverse_sql="DROP INDEX IF EXISTS startup_pitch_ivfflat_idx;"
        ),
        migrations.RunSQL(
            sql="""
            CREATE INDEX investor_mandate_ivfflat_idx
            ON ecosystem_investor
            USING ivfflat (mandate_embedding vector_cosine_ops)
            WITH (lists = 100);
            """,
            reverse_sql="DROP INDEX IF EXISTS investor_mandate_ivfflat_idx;"
        ),
    ]
"""
Example Startup model — Campus Innovation & Engagement Intelligence Hub
Copy into ecosystem/models.py before running migrations.
"""
from django.db import models
from pgvector.django import VectorField


class Startup(models.Model):
    name = models.CharField(max_length=255)
    pitch_summary = models.TextField(blank=True)
    pitch_embedding = VectorField(dimensions=384, null=True, blank=True)

    class Meta:
        app_label = "ecosystem"
        db_table = "ecosystem_startup"

    def __str__(self):
        return self.name

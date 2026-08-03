# matching/apps.py
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class MatchingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "matching"
    verbose_name = "Ecosystem Matching Engine"

    def ready(self):
        """
        Pre-load the embedding model at startup to ensure the first request 
        doesn't suffer from high latency.
        """
        # Avoid loading in management commands or secondary processes
        import sys
        if 'runserver' in sys.argv:
            try:
                from .embeddings import get_model
                get_model()
                logger.info("Matching Engine: all-MiniLM-L12-v2 pre-loaded successfully.")
            except Exception as e:
                logger.error(f"Matching Engine: Failed to load model on startup: {e}")
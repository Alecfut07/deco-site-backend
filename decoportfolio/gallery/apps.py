from django.apps import AppConfig
from django.db.models.signals import post_migrate
import logging

logger = logging.getLogger(__name__)

class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'

    def ready(self):
        from .signals import ensure_family_group_exists
        import gallery.signals # This ensures signals are loaded

        post_migrate.connect(
            ensure_family_group_exists,
            sender=self,
            dispatch_uid="gallery.ensure_family_group_exists",
        )
        logger.info("gallery ready() called and post_migrate signal connected.")

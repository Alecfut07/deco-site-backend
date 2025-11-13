from django.apps import AppConfig


class GalleryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gallery'

    def ready(self):
        from django.db.models.signals import post_migrate
        from .signals import ensure_family_group_exists
        import gallery.signals # This ensures signals are loaded

        post_migrate.connect(ensure_family_group_exists, sender=self)

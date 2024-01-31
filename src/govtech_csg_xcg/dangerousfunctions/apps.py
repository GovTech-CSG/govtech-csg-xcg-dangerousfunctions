from django.apps import AppConfig

from .patch.patch import Patcher


class RbacConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "govtech_csg_xcg.dangerousfunctions"

    def ready(self):
        Patcher.do_patch()

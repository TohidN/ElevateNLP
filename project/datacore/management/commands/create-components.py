from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create Dynamic Linguistics Components"

    def handle(self, *args, **options):
        import os

        from django.conf import settings

        from datacore.models import Component

        def get_component(code, include_self=False):
            coms = (
                Component.objects.get(code=code)
                .get_descendants(include_self=include_self)
                .values("code", "title")
            )
            com_result = f'{code.replace("-","_")} = [\n'
            for com in coms:
                com_result = (
                    com_result + f'\t("{com.get("code")}", "{com.get("title")}"),\n'
                )
            com_result = com_result + "]\n\n"
            return com_result

        path = os.path.join(settings.BASE_DIR, "datacore/components.py")
        if os.path.exists(path):
            os.remove(path)

        f = open(path, "a")
        f.write(get_component(code="INSTANCE"))
        f.write(get_component(code="MORPHEME", include_self=True))
        f.write(get_component(code="POS"))
        f.write(get_component(code="PHRASE"))
        f.write(get_component(code="WORD_COLLECTION"))
        f.write(get_component(code="RELATION"))
        f.close()

        # End Test
        self.stdout.write(self.style.SUCCESS("Import Finished."))

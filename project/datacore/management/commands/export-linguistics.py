from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Export Linguistics Data"

    def handle(self, *args, **options):
        import json
        import os

        from django.conf import settings
        from mptt.templatetags.mptt_tags import cache_tree_children

        from datacore.models import Component

        # Recursive tree to handle nested components
        def get_component_children(component, level):
            if level == 0:
                children = Component.objects.all()
                children = cache_tree_children(children)
            else:
                children = Component.get_children(component)
            index = 0
            child_data = {}
            for child in children:
                child_data[index] = {}
                child_data[index]["title"] = child.title
                child_data[index]["description"] = child.description
                child_data[index]["code"] = child.code
                child_data[index]["codes"] = child.codes
                child_data[index]["component_type"] = child.component_type
                child_data[index]["references"] = {}
                r_count = 0
                for reference in child.references.all():
                    child_data[index]["references"][r_count] = {
                        "title": reference.title,
                        "description": reference.description,
                        "url": reference.url,
                    }

                child_data[index]["data"] = child.data
                child_data[index]["children"] = get_component_children(
                    child, level=level + 1
                )
                index = index + 1
            return child_data

        # Convert linguistic components data to json
        data = get_component_children(component=None, level=0)

        # Write to Json file
        path = os.path.join(
            settings.BASE_DIR, "../dataset/linguistics/dump_json_components_new.json"
        )
        with open(path, "w") as outfile:
            json.dump(data, outfile)

        # OPTIONAL: it helps prevent problems regarding item orders and tree representation in admin menu
        Component.objects.rebuild()

        self.stdout.write(self.style.SUCCESS("Task Finished."))

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Import Linguistics Data"

    def handle(self, *args, **options):
        import json
        import os

        from datacore.models import Component, Reference
        from django.conf import settings

        # Reading file and loading JSON content
        path = os.path.join(
            settings.BASE_DIR, "../dataset/linguistics/dump_json_components_new.json"
        )
        content = open(path, "r").read()
        data = json.loads(content)

        # Import Linguistics Data
        def import_data(data, parent):
            for key, item in data.items():
                com = Component(
                    title=item["title"],
                    description=item["description"],
                    parent=parent,
                    code=item["code"],
                    codes=item["codes"],
                    component_type=item["component_type"],
                    data=item["data"],
                )
                com.save()
                if len(item["references"]) > 0:
                    for key, reference in item["references"].items():
                        ref, created = Reference.objects.get_or_create(
                            title=reference["title"],
                            url=reference["url"],
                            description=reference["description"],
                        )
                        com.references.add(ref)
                if len(item["children"]) > 0:
                    import_data(data=item["children"], parent=com)

        import_data(data=data, parent=None)

        # import csv
        # with open(os.path.join(settings.BASE_DIR, '../dataset/linguistics/com.csv'), 'r') as file:
        # 	reader = csv.reader(file)
        # 	for row in reader:
        # 		com = Component(title=row[], description=row[], parent=None, code=row[], codes=row[], component_type=row[], url=row[], data=row[])
        # 		com.save()

        # syntatic = Component.objects.get_or_create(title="Syntatic", code="syntatic")[0]
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-POS-Tags.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # pos = Component.objects.create(title="Part Of Speech", code="pos", parent=syntatic)
        # for rel in data:
        # 	pos_tag = Component(title=data[rel]["title"], code=rel, parent=pos)
        # 	if "url" in data[rel]: pos_tag.url=[data[rel]["url"]]
        # 	if "description" in data[rel]: pos_tag.description=data[rel]["description"]
        # 	if "ud-code" in data[rel]: pos_tag.ud_code=data[rel]["ud-code"]
        # 	pos_tag.save()
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-Features.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # uf = Component.objects.create(title="Morphosyntactic Property", code="syn", parent=syntatic)
        # for rel in data:
        # 	feature = Component(title=data[rel]["title"], code=rel, ud_code=data[rel]["ud-code"], description=data[rel]["description"], url=[data[rel]["url"]], parent=uf)
        # 	data[rel]["types"]: feature.feat_types=data[rel]["types"]
        # 	feature.save()
        # 	if data[rel]["values"]:
        # 		for value in data[rel]["values"]:
        # 			sub_feature = Component.objects.create(title=value, code=value, ud_code=value, parent=feature)
        # 			sub_feature.save()
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-Dep-Rel.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # udp = Component.objects.create(title="Universal Features", code="uf", parent=syntatic)
        # for rel in data:
        # 	d_relation = Component(title=data[rel]["title"], code=rel, ud_code=data[rel]["ud-code"], description=data[rel]["description"], url=[data[rel]["url"]], parent=udp)
        # 	d_relation.save()
        #
        # #import word relationship types(Morphological Paterns)
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/morpheme-types.json')
        # data = json.loads(open(path, "r").read())
        # mr = Component.objects.create(title="Morphosemantic Relationship", code="mr", parent=syntatic)
        # for item in data:
        # 	main_relation = Component.objects.get_or_create(title=data[item]["type"][1], parent=mr)
        # 	w_relation = Component(title=data[item]["title"], code=item, parent=main_relation[0])
        # 	if data[item]["url"]: w_relation.url = [data[item]["url"]]
        # 	w_relation.save()
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/morpheme-types-custom.json')
        # data = json.loads(open(path, "r").read())
        # for item in data:
        # 	w_relation = WordRelation(title=data[item]["title"], source=data[item]["version"], source_version=data[item]["version"])
        # 	if data[item]["type"]: w_relation.relation_type = [data[item]["type"]]
        # 	if data[item]["url"]: w_relation.url = [data[item]["url"]]
        # 	w_relation.save()
        #
        #
        #
        # PosTag.objects.all().delete()
        # Feature.objects.all().delete()
        # DependencyRelation.objects.all().delete()
        # WordRelation.objects.all().delete()
        #
        # print("\n\nImport Started.\n___________________________________")
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-POS-Tags.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # for rel in data:
        # 	pos_tag = PosTag(title=data[rel]["title"], code=rel)
        # 	if "url" in data[rel]: pos_tag.url=data[rel]["url"]
        # 	if "description" in data[rel]: pos_tag.description=data[rel]["description"]
        # 	if "ud-code" in data[rel]: pos_tag.ud_code=data[rel]["ud-code"]
        # 	if "type" in data[rel]: pos_tag.pos_type = "o" if data[rel]["type"]=="Open Class" else "c" if data[rel]["type"]=="Close Class" else "x"
        # 	pos_tag.save()
        #
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-Features.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # for rel in data:
        # 	feature = Feature(title=data[rel]["title"], code=rel, ud_code=data[rel]["ud-code"], description=data[rel]["description"], url=data[rel]["url"])
        # 	if data[rel]["values"]: feature.feat_values=data[rel]["values"]
        # 	if data[rel]["types"]: feature.feat_types=data[rel]["types"]
        # 	feature.save()
        #
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/Universal-Dep-Rel.json')
        # content = open(path, "r").read()
        # data = json.loads(content)
        # for rel in data:
        # 	d_relation = DependencyRelation(title=data[rel]["title"], code=rel, ud_code=data[rel]["ud-code"], description=data[rel]["description"], url=data[rel]["url"])
        # 	d_relation.save()
        #
        # # import word relationship types(Morphological Paterns)
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/morpheme-types.json')
        # data = json.loads(open(path, "r").read())
        # for item in data:
        # 	w_relation = WordRelation(title=data[item]["title"], source=data[item]["version"], source_version=data[item]["version"])
        # 	if data[item]["type"]: w_relation.relation_type = [data[item]["type"]]
        # 	if data[item]["url"]: w_relation.url = [data[item]["url"]]
        # 	w_relation.save()
        #
        # path = os.path.join(settings.BASE_DIR, '../dataset/linguistics/morpheme-types-custom.json')
        # data = json.loads(open(path, "r").read())
        # for item in data:
        # 	w_relation = WordRelation(title=data[item]["title"], source=data[item]["version"], source_version=data[item]["version"])
        # 	if data[item]["type"]: w_relation.relation_type = [data[item]["type"]]
        # 	if data[item]["url"]: w_relation.url = [data[item]["url"]]
        # 	w_relation.save()

        # End Test
        self.stdout.write(self.style.SUCCESS("Import Finished."))

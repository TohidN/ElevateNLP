from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Test Things"

    def handle(self, *args, **options):
        import json
        import os

        from django.conf import settings
        from tqdm.auto import tqdm

        from datacore.models import (Corpora, DataSource, Document, Language,
                                     Phrase, PhraseCollection, Reference,
                                     Template)

        # create language, data_source and it's Reference links
        Reference, created = Reference.objects.get_or_create(
            title="Squad 2 - official homepage",
            url="https://rajpurkar.github.io/SQuAD-explorer/explore/v2.0/dev/",
            description="Squad's homepage",
        )
        data_source, created = DataSource.objects.get_or_create(
            title="SQuAD", version="2"
        )
        data_source.references.add(Reference)
        english, created = Language.objects.get_or_create(
            en_name="English", native_name="English", alpha2="en"
        )

        # OPTIONAL: Delete old imports
        Document.objects.filter(data_sources__id=data_source.id).delete()

        # Create corpora
        squad, created = Corpora.objects.get_or_create(title="SQuAD 2")
        squad.data_sources.add(data_source)

        # Loading Files.
        path = os.path.join(settings.BASE_DIR, "../dataset/SQuAD/train-v2.0.json")
        f = open(path, "r")
        content = f.read()
        data = json.loads(content)

        # Importing data.
        for doc in tqdm(data["data"], desc="Documents"):
            doc_title = doc["title"].replace("_", " ")
            document = Document.objects.create(title=doc_title, language=english)
            document.data_sources.add(data_source)
            questions = PhraseCollection.objects.create(
                title=f"Questions for '{doc_title}' document"
            )
            questions.data_sources.add(data_source)
            questions.save()
            raw_text = ""
            for par in tqdm(doc["paragraphs"], desc="Questions", leave=False):
                raw_text = "\n".join([raw_text, par["context"]])
                # import questions
                for qas in par["qas"]:
                    question, created = Phrase.objects.get_or_create(
                        text=qas["question"], language=english
                    )
                    questions.phrases.add(question)
            document.content = raw_text
            document.phrase_collections.add(questions)
            document.save()
            squad.documents.add(document)

        self.stdout.write(self.style.SUCCESS("Task Finished."))

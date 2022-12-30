import json
import os

import stanza
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from datacore.models import Document, Phrase, PhraseCollection, Template


class Command(BaseCommand):
    help = "Import Tatoeba Dataset"

    def handle(self, *args, **options):
        import os

        import pandas as pd
        from django.conf import settings
        from tqdm.auto import tqdm

        from datacore.functions.stanza import get_stanza
        from datacore.models import (Document, Phrase, PhraseCollection,
                                     Template)

        # set up NLP pipeline
        nlp = get_stanza(lang="en", processors="tokenize")

        Reference1, created = Reference.objects.get_or_create(
            title="Tatoeba - official homepage",
            url="https://tatoeba.org/en",
            description="Tatoeba is a collection of sentences and translations.It's collaborative, open, free and even addictive.",
        )
        Reference2, created = Reference.objects.get_or_create(
            title="Tatoeba - Dataset",
            url="https://tatoeba.org/en/downloads",
            description="Tatoeba dataset.",
        )
        data_source, created = DataSource.objects.get_or_create(title="Tatoeba")
        data_source.references.add(Reference1, Reference2)

        tatoeba, created = PhraseCollection.objects.get_or_create(
            title="Tatoeba Phrases xxx"
        )
        tatoeba.data_sources.add(data_source)

        print("Loading dataset...")
        path = os.path.join(settings.BASE_DIR, "../dataset/tatoeba/sentences.csv")
        df = pd.read_csv(
            path,
            encoding="utf-8",
            sep="\t",
            header=None,
            usecols=[1, 2],
            names=["language", "sentence"],
        )
        df.info()
        df.head()

        # OPTIONAL: Only import english sentences
        df = df[df.language == "eng"]

        # Import phrases
        for row in tqdm(df.iterrows(), total=len(df)):
            try:
                # Import phrases in all languages or in a specific language using alpha3 code in row[1]
                doc = nlp(row[1]["sentence"])
                for sentence in doc.sentences:
                    phrase, created = Phrase.objects.get_or_create(text=sentence.text)
                    tatoeba.phrases.add(phrase)
            except Exception as e:
                print(
                    f"error in importing row #{row.index()} with data: {row[1]}\nError: {e}\n"
                )

        self.stdout.write(self.style.SUCCESS("Task Finished."))

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import proverbs, idioms, expresions and sayings"

    def handle(self, *args, **options):
        """
        Import proverbs, idioms, expresions and sayings
        """
        import os

        import pandas as pd
        from django.conf import settings
        from tqdm.auto import tqdm

        from datacore.models import (Component, DataSource, Language, Phrase,
                                     Reference)

        # Preparing and Reading Dataset
        title = "Proverbs, idioms, expresions and sayings"
        proveb = "PROVERB"  # code for linguistic component, other options which can be used are Idiom,
        english, created = Language.objects.get_or_create(
            en_name="English", native_name="English", alpha2="en"
        )
        data_source, created = DataSource.objects.get_or_create(
            title=title, version="13"
        )
        Reference1, created = Reference.objects.get_or_create(
            title=title + " - scrapping source",
            url="https://www.kaggle.com/code/bryanb/scraping-sayings-and-proverbs#PART-I:-Scraping-English-sayings",
            description="Source Code for scrapping data from web",
        )
        Reference2, created = Reference.objects.get_or_create(
            title=title + " - scrapping data",
            url="https://www.kaggle.com/code/bryanb/scraping-sayings-and-proverbs#PART-I:-Scraping-English-sayings",
            description="Data Source for scrapping data from web",
        )
        data_source.references.add(Reference1, Reference2)
        collection, created = PhraseCollection.objects.get_or_create(title=title)
        collection.data_sources.add(data_source)

        sayings = os.path.join(
            settings.BASE_DIR,
            "../dataset/sayings, proverbs, idioms/English_phrases_and_sayings.csv",
        )

        # Reading File
        sayings = os.path.join(
            settings.BASE_DIR,
            "../dataset/sayings, proverbs, idioms/English_phrases_and_sayings.csv",
        )
        df = pd.read_csv(sayings)

        # Importing Dataset
        for row in tqdm(df.iterrows(), total=len(df)):
            try:
                phrase, create = Phrase.objects.get_or_create(
                    text=" ".join(row[1]["text"].split()), language=english
                )
                phrase.data["description"] = " ".join(row[1]["explanation"].split())
                phrase.save()
            except:
                print(" ".join(row[1]["text"].split()))
            collection.phrases.add(phrase)

        self.stdout.write(self.style.SUCCESS("Task Finished."))

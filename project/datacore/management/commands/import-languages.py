from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Import Languages"

    def handle(self, *args, **options):
        import json
        import os

        import pandas as pd
        from django.conf import settings
        from tqdm.auto import tqdm

        from datacore.models import Language

        # Importing Languages.
        # import alpha2, alpha3b, en_name
        lang_file = os.path.join(
            settings.BASE_DIR,
            "../dataset/languages/language-codes/archive/language-codes-3b2.csv",
        )
        df = pd.read_csv(lang_file, encoding="utf-8", sep=",")

        for row in tqdm(df.iterrows(), total=len(df)):
            language, created = Language.objects.get_or_create(alpha2=row[1]["alpha2"])
            language.alpha3b = row[1]["alpha3-b"]
            language.en_name = row[1]["English"]
            language.save()

        # import alpha3t and less used languages
        lang_file = os.path.join(
            settings.BASE_DIR,
            "../dataset/languages/language-codes/archive/language-codes-full.csv",
        )
        df = pd.read_csv(lang_file, encoding="utf-8", sep=",")
        df.fillna("", inplace=True)

        for row in tqdm(df.iterrows(), total=len(df)):
            try:
                if row[1]["alpha2"] != "":
                    language = Language.objects.get(alpha2=row[1]["alpha2"])
                    if row[1]["alpha3-t"] != "":
                        language.alpha3t = row[1]["alpha3-t"]
                        language.save()
                else:
                    language = Language(
                        alpha3b=row[1]["alpha3-b"], en_name=row[1]["English"]
                    )
                    language.save()
            except:
                tqdm.write(f"Error in importing row: {row[1]}")

        # import custom data(for now: language in native and number of speakers)
        lang_file_json = os.path.join(
            settings.BASE_DIR, "../dataset/languages/languages.json"
        )
        lang_data_json = json.loads(
            open(lang_file_json, "rb").read().decode("utf-8-sig")
        )
        for lang in tqdm(lang_data_json):
            try:
                language = Language.objects.get(alpha2=lang)
                if "speakers" in lang_data_json[lang]:
                    language.native_speakers = lang_data_json[lang]["speakers"]
                language.native_name = lang_data_json[lang]["nativeName"]
                language.save()
            except:
                print(f"Error in importing: {lang_data_json[lang]}")

        # TODO: import dialect, territory, and other language data from ietf-language-tags.csv and it's link to 'core' dataset
        # TODO: locations can be imported from http://www.geonames.org/
        self.stdout.write(self.style.SUCCESS("Task Finished."))

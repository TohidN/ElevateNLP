from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Setup project"

    print("\n~~~ 1. Downloading NLTK resources:")
    import nltk

    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("omw-1.4")

    print("\n~~~ 2. Downloading Santza resources:")
    import stanza

    stanza.download("en")  # download English model

    print("\n~~~ 3. Downloading Spacy's  `en_core_web_sm model`:")
    import spacy

    spacy.cli.download("en_core_web_sm")

    print("\n~~~ Finished Setup")

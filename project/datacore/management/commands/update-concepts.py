import json
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from datacore.functions import covert_attribute_to_pos
from datacore.models import Concept, Document, Phrase, Template


class Command(BaseCommand):
    help = "Update concepts in phrases"

    def handle(self, *args, **options):
        print("\n\n\n\n\nStarted.\n___________________________________")
        all_phrases = Phrase.objects.all()
        for phrase in all_phrases:
            for key, phrase_lemma in phrase.parsed_data.items():
                lemma = phrase_lemma["lemma"]
                # Rule 1: if only one concept exist for a lemma then that is lemma's concept
                concepts = Concept.objects.filter(synonyms__text=lemma)
                if len(concepts) == 1:
                    phrase.parsed_data[key]["concepts"] = {
                        0: {
                            "concept": concepts[0].id,
                            "probability": 1,
                            "reason": "only concept",
                        }
                    }
                else:
                    phrase.parsed_data[key]["concepts"] = {}
                # one or more concepts with same POS
                if len(concepts) > 1:
                    counter = 0
                    for concept in concepts:
                        if (
                            covert_attribute_to_pos(attribute=concept.attribute)
                            == phrase.parsed_data[key]["pos"]
                        ):
                            phrase.parsed_data[key]["concepts"][counter] = {
                                "concept": concept.id,
                            }
                            counter = counter + 1
                    if counter == 0:
                        phrase.parsed_data[key]["concepts"] = {}
                    # Rule 2: of only one concept with the same POS as lemma exist then that is lemma's concept
                    if counter == 1:
                        phrase.parsed_data[key]["concepts"][0]["probability"] = 1
                        phrase.parsed_data[key]["concepts"][0][
                            "reason"
                        ] = "only concept with same POS"
                    # Rule 3: more concepts with the same POS as lemma exist
                    elif counter > 1:
                        probability = 1 / counter
                        for ckey, concept in phrase.parsed_data[key][
                            "concepts"
                        ].items():
                            phrase.parsed_data[key]["concepts"][ckey][
                                "probability"
                            ] = probability
                            phrase.parsed_data[key]["concepts"][ckey][
                                "reason"
                            ] = "{} possible concepts".format(counter)
            phrase.save()

        # End Test
        self.stdout.write(
            self.style.SUCCESS("___________________________________\nTest Finished.")
        )
        import winsound

        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 2000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)

import stanza
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

from datacore.functions.utils import strip_word
from datacore.models import (Component, Language, Lemma, NamedEntity, Phrase,
                             PhraseAnalysis, Template, Word)


class Command(BaseCommand):
    help = "Batch Analyze Sentences"

    def handle(self, *args, **options):
        """
        Analyze phrases
        This functions seperates stanza pipelines for 'ner' and other pipelines since running full pipeline can cause memory issues in low-memory hardware.
        Other pipelines are not seperated since 'deprel' pipeline has all other pipelines as it's requirements.
        for full analysis on a phrase run phrase analyze
        """
        analyzer = "stanza"
        phrase_items = Phrase.objects.filter(
            phraseanalysis=None
        )  # phrases without analysis
        # phrase_items = Phrase.objects.filter(pk__gte=227186)
        # PhraseAnalysis.objects.filter(phrase_id__gte=227186).delete()

        print("1. Tokenize, POS, XPOS, UFeats, Lemmatization, and DepRel")
        # analyze phrase: Tokenize & POS
        nlp = stanza.Pipeline(
            lang="en",
            processors="tokenize,mwt,pos,lemma,depparse",
            tokenize_no_ssplit=True,
        )
        for phrase_item in phrase_items:
            analysis, created = PhraseAnalysis.objects.get_or_create(
                phrase=phrase_item, analyzer=analyzer
            )
            analysis.save()
            language = phrase_item.language
            doc = nlp(phrase_item.text)
            phrase = doc.sentences[0]

            data = {}
            pos_template = []
            xpos_template = []
            feat_template = []
            for word in phrase.words:
                word_text = strip_word(word.text)
                word_id = str(word.id)
                # create word object
                word_obj, created = Word.objects.get_or_create(
                    text=word_text, language=language
                )
                if created:
                    word_obj.text_length = len(word.text)
                # add word to phrases words_list and if it's new add it to frequency distribution counter
                if word_text.lower() not in phrase_item.words_list:
                    phrase_item.words_list.append(word_text.lower())
                    phrase_item.save()
                    word_obj.frequency_distribution = (
                        word_obj.frequency_distribution + 1
                    )
                # save word object
                word_obj.save()
                analysis.words.add(word_obj)
                # Tokenize and POS process
                data[word_id] = {}
                data[word_id]["id"] = word.id
                data[word_id]["text"] = word_text
                data[word_id]["upos"] = word.upos
                data[word_id]["xpos"] = word.xpos
                data[word_id]["start_char"] = word.start_char
                data[word_id]["end_char"] = word.end_char
                if word.feats is not None:
                    word_feats = {}
                    for feat in str(word.feats).split("|"):
                        splited = feat.split("=")
                        word_feats[splited[0]] = splited[1]
                        data[word_id]["feats"] = word_feats
                    # template list items
                    pos_template.append(word.pos)
                    xpos_template.append(
                        "{}({})".format(word.pos, word.xpos) if word.xpos else word.pos
                    )
                    feat_template.append(
                        "{}({}~{})".format(word.pos, word.xpos, word.feats)
                    )
                # Lemmatization Process
                data[word_id]["lemma"] = word.lemma
                if (
                    word.lemma != word.text and word.lemma != None
                ):  # if word has a lemma add it to list
                    lemma_obj, created = Lemma.objects.get_or_create(
                        text=word.lemma, language=language
                    )
                    lemma_obj.text_length = len(word.lemma)
                    lemma_obj.source = ""
                    lemma_obj.source_version = ""
                    # add lemma to phrases lemmas_list and if it's new add it to frequency distribution counter
                    if word.lemma.lower() not in phrase_item.lemmas_list:
                        phrase_item.lemmas_list.append(word.lemma.lower())
                        lemma_obj.frequency_distribution = (
                            word_obj.frequency_distribution + 1
                        )
                    lemma_obj.save()
                    # add this lemma as word's lemma
                    word_obj.lemma = lemma_obj
                    word_obj.save()
                # Dependency Parsing Process
                data[word_id]["deprel_id"] = word.head
                data[word_id]["deprel"] = word.deprel
            # Create template string
            pos_template = "-".join(pos_template)
            xpos_template = "-".join(xpos_template)
            feat_template = "-".join(feat_template) if feat_template is not None else ""
            # Create delrel template string
            dep_list = []
            for dep in phrase.dependencies:
                dep_list.append(
                    "({},{},{},{})".format(
                        dep[2].id, dep[2].pos, dep[2].deprel, dep[0].id
                    )
                )
            dep_template = "-".join(dep_list)
            # Create templates
            template, created = Template.objects.get_or_create(
                pos=pos_template, parent=None
            )
            new_template, created = Template.objects.get_or_create(
                pos=pos_template,
                xpos=xpos_template,
                feats=feat_template,
                dep=dep_template,
                parent=template,
            )
            analysis.template = new_template
            analysis.data = data

            analysis.save()
        print("2. Named Entities.")
        # Dependency Relations
        nlp = stanza.Pipeline(
            lang="en", processors="tokenize,mwt,ner", tokenize_no_ssplit=True
        )
        for phrase_item in phrase_items:
            analysis, created = PhraseAnalysis.objects.get_or_create(
                phrase=phrase_item, analyzer=analyzer
            )
            doc = nlp(phrase_item.text)
            phrase = doc.sentences[0]

            for token in phrase.tokens:
                analysis.data[str(token.id[0])]["ner"] = token.ner

            for item in phrase.ents:
                try:
                    entity_type = Component.objects.filter(Q(codes__ud=item.type))[0]
                except Component.DoesNotExist:
                    entity_type = Component.objects.get(code="INSTANCE")[
                        0
                    ]  # root it used for unknown items
                entity, created = NamedEntity.objects.get_or_create(
                    text=item.text, ne_type=entity_type
                )

                if entity.text.lower() not in phrase_item.entities_list:
                    phrase_item.entities_list.append(entity.text.lower())
                    entity.frequency_distribution = entity.frequency_distribution + 1

                entity.save()
                analysis.entities.add(entity)
            analysis.save()

        self.stdout.write(
            self.style.SUCCESS("Successfully finished Language import task.")
        )
        import winsound

        frequency = 2500  # Set Frequency To 2500 Hertz
        duration = 2000  # Set Duration To 1000 ms == 1 second
        winsound.Beep(frequency, duration)

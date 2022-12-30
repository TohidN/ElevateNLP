import re

from django.core.management.base import BaseCommand, CommandError
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer

from datacore.models import (Component, Concept, DataSource, Definition,
                             DomainOntology, Example, Language, Reference,
                             Relation, Word, WordRelation, WordRelationType)


class Command(BaseCommand):
    help = "Import WordNet"

    def handle(self, *args, **options):
        import re

        from nltk.corpus import wordnet as wn
        from nltk.stem import WordNetLemmatizer
        from tqdm.auto import tqdm

        from datacore.models import (Component, Concept, Definition, Example,
                                     Language, Relation, Word, WordCollection)

        # Prepare data and lemmatizer
        lemmatizer = WordNetLemmatizer()

        english, created = Language.objects.get_or_create(
            en_name="English", native_name="English", alpha2="en"
        )
        antonym, created = WordRelationType.objects.get_or_create(
            title="Antonym",
            descriptor="is opposite of",
            reverse_descriptor="is opposite of",
            direction_type="u",
        )
        pertainym, created = WordRelationType.objects.get_or_create(
            title="Pertainym",
            descriptor="is pertaining to",
            reverse_descriptor="is pertaining to",
            direction_type="u",
        )
        derivationally_related_forms, created = WordRelationType.objects.get_or_create(
            title="Derivationally Related Form",
            descriptor="is derivationally related to",
            reverse_descriptor="is derivationally related to",
            direction_type="u",
        )

        Reference1, created = Reference.objects.get_or_create(
            title="WordNet - official homepage",
            url="shttps://wordnet.princeton.edu/",
            description="",
        )
        Reference2, created = Reference.objects.get_or_create(
            title="NLTK WordNet",
            url="https://www.nltk.org/howto/wordnet.html",
            description="",
        )
        data_source, created = DataSource.objects.get_or_create(
            title="WordNet", version=wn.get_version()
        )
        data_source.references.add(Reference1, Reference2)

        ontology, created = DomainOntology.objects.get_or_create(
            title="WordNet Upper Ontology"
        )

        synset_count = 0
        for synset in wn.all_synsets():
            synset_count += 1

        # Importing wordnet concepts, lemmas(Synonyms and Antonyms), definitions and examples.
        for synset in tqdm(wn.all_synsets(), total=synset_count):
            concept = Concept(
                pos=Component.get_by_wn(synset.pos()).code,
                source_offset=synset.offset(),
                ontology_domain=ontology,
            )
            concept.save()
            concept.data_sources.add(data_source)
            # add definition
            definition = Definition(
                concept=concept, text=synset.definition(), language=english
            )
            definition.save()
            definition.data_sources.add(data_source)
            # add examples
            if synset.examples():
                for ex in synset.examples():
                    example = Example(concept=concept, text=ex, language=english)
                    example.save()
                    example.data_sources.add(data_source)
                    if synset.lemmas():
                        for lemma in synset.lemmas():
                            if (
                                lemma.name() in ex
                                or lemmatizer.lemmatize(lemma.name()) in ex
                            ):
                                lemma_name = lemma.name().replace("_", " ")
                                obj_word, create = Word.objects.get_or_create(
                                    text=lemma_name, language=english
                                )
                                example.word = obj_word

            # add lemmas(synonyms) and lexical relations(antonyms(), derivationally_related_forms(), and pertainyms())
            if synset.lemmas():
                for lemma in synset.lemmas():
                    lemma_name = lemma.name().replace("_", " ")
                    # store multi-words in a single collection, while creating Word objects from it's components
                    words = re.split(r"\s+|-|/", lemma_name.lower())
                    word_list = []
                    for word in words:
                        new_word, created = Word.objects.get_or_create(
                            text=word, language=english
                        )
                        word_list.append(new_word.id)
                    if len(words) > 1:
                        word_collection = WordCollection(
                            words=word_list, collection_type="SEMANTIC-NGRAM"
                        )
                    # Add Synonyms
                    lemma_obj, created = Word.objects.get_or_create(
                        text=lemma_name, language=english
                    )
                    concept.synonyms.add(lemma_obj)
                    # Add Antonyms
                    if lemma.antonyms():
                        for lemma in lemma.antonyms():
                            # prepare and import antonym's lemma to database
                            antonym_lemma_name = lemma.name().replace("_", " ")
                            antonym_obj, created = Word.objects.get_or_create(
                                text=antonym_lemma_name, language=english
                            )
                            concept.antonyms.add(antonym_obj)
                            # create word relation for antonym
                            if (
                                WordRelation.objects.filter(
                                    words__contains=[lemma_obj.id, antonym_obj.id],
                                    word_relation=antonym,
                                ).exists()
                                == False
                            ):
                                word_rel = WordRelation(
                                    words=[lemma_obj.id, antonym_obj.id],
                                    word_relation=antonym,
                                )
                                word_rel.save()
                    # add pertainyms
                    if lemma.pertainyms():
                        for lemma in lemma.pertainyms():
                            # prepare and import antonym's lemma to database
                            pertainym_lemma_name = lemma.name().replace("_", " ")
                            pertainym_obj, created = Word.objects.get_or_create(
                                text=pertainym_lemma_name, language=english
                            )
                            # create word relation for antonym
                            if (
                                WordRelation.objects.filter(
                                    words__contains=[lemma_obj.id, pertainym_obj.id],
                                    word_relation=pertainym,
                                ).exists()
                                == False
                            ):
                                word_rel = WordRelation(
                                    words=[lemma_obj.id, pertainym_obj.id],
                                    word_relation=pertainym,
                                )
                                word_rel.save()
                    # Add derivationally_related_forms
                    if lemma.derivationally_related_forms():
                        for lemma in lemma.derivationally_related_forms():
                            # prepare and import derivitive's lemma to database
                            derivitive_lemma_name = lemma.name().replace("_", " ")
                            derivitive_obj, created = Word.objects.get_or_create(
                                text=derivitive_lemma_name, language=english
                            )
                            # create word relation for antonym
                            if (
                                WordRelation.objects.filter(
                                    words__contains=[lemma_obj.id, derivitive_obj.id],
                                    word_relation=derivationally_related_forms,
                                ).exists()
                                == False
                            ):
                                word_rel = WordRelation(
                                    words=[lemma_obj.id, derivitive_obj.id],
                                    word_relation=derivationally_related_forms,
                                )
                                word_rel.save()

        # Importing concept relationships
        from datacore.components import RELATION

        def add_relation(synset, relations, code):
            if relations:
                for rel in relations:
                    target = Concept.objects.get(
                        data_sources__id=data_source.id,
                        source_offset=rel.offset(),
                        pos=Component.get_by_wn(rel.pos()).code,
                    )
                    Relation.objects.create(
                        concepts=[target.pk, syn_obj.pk], relation_type=code
                    )

        for synset in tqdm(wn.all_synsets(), total=synset_count):
            # Get Synset from 'Concept' model
            syn_obj = Concept.objects.get(
                data_sources__id=data_source.id,
                source_offset=synset.offset(),
                pos=Component.get_by_wn(synset.pos()).code,
            )
            """
			hypernyms and hyponyms, indicate being a kind of something else, or being an instance of something else
			- hypernyms, instance_hypernyms
			- hyponyms, instance_hyponyms
			"""
            # Hyponym: (hyponyms) is a kind of (synset)
            # Hypernym: (Hypernym) is a supertype of (synset)
            add_relation(synset=syn_obj, relations=synset.hyponyms(), code="HYPONYM")
            # instance_hyponyms: (instance_hyponyms) is an instance of (synset)
            # instance_hypernyms: (instance_hyponyms) has the instance (synset)
            add_relation(
                synset=syn_obj, relations=synset.instance_hyponyms(), code="INSTANCE_OF"
            )

            """
			holonyms and meronyms, indicating membership in group, having substance(s), and having part(s)
			* member_holonyms, substance_holonyms, part_holonyms
			* member_meronyms, substance_meronyms, part_meronyms
			"""
            # member_meronyms: (synset) has member (member_meronyms)
            # member_holonyms: (synset) is a member of (member_holonyms)
            add_relation(
                synset=syn_obj,
                relations=synset.member_meronyms(),
                code="MEMBER_HOLONYM",
            )
            # part_meronyms: (synset) has part (part_meronyms)
            # part_holonyms: (synset) is part of (part_holonyms)
            add_relation(
                synset=syn_obj, relations=synset.part_meronyms(), code="PART_HOLONYM"
            )
            # substance_meronyms: (synset) has substance (substance_meronyms)
            # substance_holonyms (synset) is substance of (substance_holonyms)
            add_relation(
                synset=syn_obj,
                relations=synset.substance_meronyms(),
                code="SUBSTANCE_HOLONYM",
            )
            """
			domain: topic domains, region domains, and usage domains
			topic_domains, region_domains, usage_domains
			in_topic_domains, in_region_domains, in_usage_domains 
			"""
            # topic_domains: (topic_domains) is under topic domain of (synset)
            # in_topic_domains: (in_topic_domains) is in topic domain of (synset)
            add_relation(
                synset=syn_obj,
                relations=synset.in_topic_domains(),
                code="TOPIC_DOMAINS",
            )
            # region_domains: (region_domains) is relatet to region (synset)
            # in_region_domains: (in_region_domains) region is related to (synset)
            add_relation(
                synset=syn_obj,
                relations=synset.in_region_domains(),
                code="REGION_DOMAINS",
            )
            # usage_domains: (usage_domains) linguistically is a (synset)
            # in_usage_domains: (in_usage_domains) as an example has (synset)
            add_relation(
                synset=syn_obj,
                relations=synset.in_usage_domains(),
                code="USAGE_DOMAINS",
            )

            # attributes: (synset - Adjective) has the attribute (attributes)
            if synset.pos() == "a":
                add_relation(
                    synset=syn_obj, relations=synset.attributes(), code="ATTRIBUTES"
                )
            # entailments: (synset) entailments (entailments)
            add_relation(
                synset=syn_obj, relations=synset.entailments(), code="ENTAILMENTS"
            )
            # causes: (synset) causes (causes)
            add_relation(synset=syn_obj, relations=synset.causes(), code="CAUSES")
            # also_sees: (synset) is related to (also_sees)
            add_relation(synset=syn_obj, relations=synset.also_sees(), code="ALSO_SEES")
            # also_sees: (synset) verb is grouped with (also_sees)
            add_relation(
                synset=syn_obj, relations=synset.verb_groups(), code="VERB_GROUP"
            )
            # also_sees: (synset) is similar to (also_sees)
            add_relation(
                synset=synset, relations=synset.similar_tos(), code="SIMILAR_TOS"
            )

        self.stdout.write(self.style.SUCCESS("Task Finished."))

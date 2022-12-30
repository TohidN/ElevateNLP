import functools

from django.contrib.postgres.fields import ArrayField, CICharField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import JSONField
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Analyzer(models.Model):
    """
    Any analyzer is used to analyze phrases and text. they can be manually created by user, or they are created and
    referenced when performing analysis. E.g. Stanford Stanza, Spacy, ...
    """

    title = models.CharField(max_length=256)
    version = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True, unique=False)
    references = models.ManyToManyField("Reference", related_name="analyzer_reference")

    def __str__(self):
        return self.title

    def get_slugified_title(self):
        return slugify(self.title)


class DataSource(models.Model):
    """
    Any Source of data that is used for importing or entering data
    E.g. WordNet, Squad, dbPedia, etc
    """

    title = models.CharField(max_length=256)
    version = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True, unique=False)
    references = models.ManyToManyField(
        "Reference", related_name="data_source_reference"
    )

    def __str__(self):
        return self.title


class Reference(models.Model):
    """
    References are used for data sources and linguistics components.
    """

    title = models.CharField(max_length=256, unique=False, null=False, blank=False)
    url = models.URLField(blank=True, unique=False)
    description = models.TextField(null=True, blank=True, unique=False)

    def __str__(self):
        return self.title


# Linguistic Components
class Component(MPTTModel):
    """
    Linguistic Components
    previusly this method was used to choose component in other models:
    component_type = models.ForeignKey("Component", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"pk__in":Component.objects.get(code="INSTANCE").get_descendants(include_self=False).values('pk')})
    """

    title = models.CharField(max_length=256)
    description = models.TextField(max_length=4096, null=True, blank=True, unique=False)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    slug = models.CharField(max_length=512, db_index=True, unique=True, blank=True)

    code = models.CharField(max_length=64, null=True, blank=True)  # TODO: , unique=True
    codes = JSONField(default=dict, blank=True)
    component_type = ArrayField(
        models.CharField(max_length=512), blank=True, default=list
    )

    references = models.ManyToManyField(
        "Reference", related_name="component_reference", blank=True
    )
    data = JSONField(default=dict, blank=True)

    class MPTTMeta:
        order_insertion_by = ["title"]

    def __str__(self):
        if self.component_type:
            return "{} {}".format(self.title, self.component_type)
        return self.title

    def create_tree_slug(self, slug):
        try:
            ancestors = self.get_ancestors(include_self=True)
            ancestors = [i.slug for i in ancestors]
        except Exception:
            ancestors = []
        return "/".join(ancestors)

    def save(self, *args, **kwargs):
        import itertools

        self.slug = (
            slugify(self.code.replace(":", "-"))
            if self.code
            else slugify(self.title, allow_unicode=True)
            if self.title
            else self.slug
        )
        if self.parent:
            self.slug = f"{self.parent.slug}/{self.slug}"
        for x in itertools.count(1):
            if (
                not Component.objects.filter(slug=self.slug).exists()
                and self.slug is not None
            ):
                break
            self.slug = f"{self.slug}-{x}"
        super(Component, self).save(*args, **kwargs)
        for child in self.get_children():
            child.save()
        return self

    @functools.lru_cache()
    def get_by_wn(value=None):
        # Get by wordnet key
        from django.db.models import Q

        obj = Component.objects.filter(
            Q(codes__wn=value) | Q(codes__wn__contains=value)
        )
        return obj[0]

    @functools.lru_cache()
    def get_by_ud(value=None):
        # Get by Universal Dependency key
        from django.db.models import Q

        obj = Component.objects.filter(Q(codes__ud=value))
        return obj[0]

    class Meta:
        verbose_name = _("Linguistic Component")
        verbose_name_plural = _("Linguistic Components")


class Language(models.Model):
    native_name = models.CharField(max_length=256)  # native
    en_name = models.CharField(max_length=256)  # in english
    native_speakers = models.IntegerField(default=0)  # in millions
    # 2 letter alpha-2 code
    alpha2 = models.CharField(max_length=2, null=True, blank=True, unique=True)
    # 3 letter alpha-3 bibliographic code. it's standard language identifier at the moment.
    alpha3b = models.CharField(max_length=3, null=True, blank=True, unique=True)
    # 3 letter alpha-3 terminologic code
    alpha3t = models.CharField(max_length=3, null=True, blank=True, unique=True)
    # TODO: add and import:
    # dialects = ArrayField(models.CharField(max_length=256), blank=True, default=list)
    # territory = models.CharField(max_length=2) # two digit code such as US,CA
    # allias = ArrayField(models.CharField(max_length=256), blank=True, default=list)
    data = JSONField(
        default=dict, blank=True
    )  # data such as it's translation in other languages

    def __str__(self):
        return self.get_title()

    def get_title(self):
        if self.en_name and self.native_name:
            return f"{self.en_name}({self.alpha3b}) - {self.native_name}"
        elif self.en_name:
            return f"{self.en_name}({self.alpha3b})"
        else:
            return f"{self.native_name}({self.alpha3b})"


class WordList(models.Model):
    """
    A list of words such as Stop words, Prepositional phrases, Interjections. etc.
    """

    title = models.CharField(max_length=2048, unique=False)
    description = models.TextField(default="")

    words = models.ManyToManyField("Word", blank=True)

    def __str__(self):
        return self.title


class WordRelationType(models.Model):
    """
    Relation types between words. E.g. Antonyms, abbreviation, formal, informal, depricated, dialect specific.
    Examples:
    direction_type=Undirected
            Antonyms is undirected, E.g. 'good' is antonym of 'bad', and 'bad' is antonym of 'good'.
    direction_type=Directed
            Abbreviation is directed, E.g. 'NY' is an 'abbreviation' of 'New York', but reverse is not true.
            furthermore it's reverse_title can be set to "expansion", as in 'New York' is an 'expansion' of 'NY'
    """

    DIRECTIONS = [
        ("d", "Directed"),
        ("u", "Undirected"),
    ]

    title = models.CharField(max_length=2048, unique=True)
    description = models.TextField(default="")

    # example for "Lemma" relation type using descriptor and reverse_descriptor:
    # descriptor:            <Word:buy>       "is a lemma of"   <Word:bought>
    # reverse_descriptor:    <Word:bought>    "is a form of"    <Word:buy>
    direction_type = models.CharField(
        max_length=1, choices=DIRECTIONS, null=True, blank=True
    )
    descriptor = models.CharField(max_length=2048, unique=False, blank=True)
    reverse_descriptor = models.CharField(max_length=2048, unique=False, blank=True)

    data = JSONField(
        default=dict, blank=True
    )  # data, such as it's translation in other languages

    def __str__(self):
        return self.title


class WordRelation(models.Model):
    """
    Relation between two words, defind in 'WordRelationType'
    E.g. Word<geese> is related to Word<goose> with WordRelationType<Irregular plural>
    words can be multi-words. E.g. "a priori" and "a posteriori", and "at most" and "at least" are antonyms.
    words can have morphemes. ie: backup->back,up
    """

    words = ArrayField(models.BigIntegerField(), default=list, size=2)  # Word id
    word_relation = models.ForeignKey(
        "WordRelationType", on_delete=models.SET_NULL, null=True, blank=True
    )

    data_sources = models.ManyToManyField("DataSource", blank=True)

    def __str__(self):
        return f"words: {self.words} --- relation: {self.word_relation.title}"

    def get_absolute_url(self):
        return reverse("datacore:word_relation", kwargs={"id": str(self.id)})


class Word(models.Model):
    """
    words are used in documents in many forms, linguistically each word is a "Free Morpheme", a Root, or Stem
    all words are single words, multi-words which represent an ontology class are added as lemmas
    * for now used for multi-words, lexeme, stem, and lemma
    * The stem is the part of the word that never changes even when morphologically inflected; a lemma is the base form of the word. For example, from "produced", the lemma is "produce", but the stem is "produc-". This is because there are words such as production.
    """

    text = CICharField(max_length=64)
    frequency_distribution = models.BigIntegerField(
        default=0
    )  # usage frequency in parsed text
    # Lemmas are stored as words, however whenever a word is used, it's frequency_distribution should increase
    # and whenever it's lemma is used it's lemma_frequency_distribution should increase
    lemma_frequency_distribution = models.BigIntegerField(
        default=0
    )  # usage frequency of a lemma

    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = (("text", "language"),)

    def __str__(self):
        return self.text

    @classmethod
    def filter_words(
        cls, start="", contain="", end="", sort_by=None, sort_type="asc", limit=0
    ):
        from django.db.models.functions import Length

        sort_type = sort_type if sort_type else "asc"

        valid_sort_by = ["wrd_txt", "wrd_len", "wrd_frq", "lma_frq"]
        valid_sort_type = ["asc", "dsc"]
        if sort_by and sort_by not in valid_sort_by:
            raise Exception(
                f"Please enter a valid sort_by parameter from {valid_sort_by} or leave empty to ignore sort. current value is `{sort_by}`."
            )
        if sort_type not in valid_sort_type:
            raise Exception(
                f"Please enter a valid sort_type parameter from {valid_sort_type}. current value is `{sort_type}`."
            )

        queryset = cls.objects
        if len(start) > 0:
            queryset = queryset.filter(text__startswith=start)
        if len(contain) > 0:
            queryset = queryset.filter(text__contains=contain)
        if len(end) > 0:
            queryset = queryset.filter(text__endswith=end)

        if sort_by:
            if sort_by == "wrd_txt":
                queryset = queryset.order_by("text" if sort_type == "asc" else "-text")
            if sort_by == "wrd_len":
                queryset = queryset.order_by(
                    Length("text") if sort_type == "asc" else Length("text").desc(),
                    "text",
                )
            if sort_by == "wrd_frq":
                queryset = queryset.order_by(
                    "frequency_distribution"
                    if sort_type == "asc"
                    else "-frequency_distribution",
                    "text",
                )
            if sort_by == "lma_frq":
                queryset = queryset.order_by(
                    "lemma_frequency_distribution"
                    if sort_type == "asc"
                    else "-lemma_frequency_distribution",
                    "text",
                )
        queryset = queryset.all()[:limit] if limit and limit > 0 else queryset
        return queryset


class NamedEntity(MPTTModel):
    """
    Named Entities extracted from text analysis and NER.
    instances of an ontology class are stored in 'Concept' model with relation to it's type with 'INSTANCE_OF' as it's relation type.
    """

    text = CICharField(max_length=2048)
    # Entity's children are abbreviations, commonly used alternatives or translation of an entity in a different language
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="ne_children",
    )
    from datacore.components import INSTANCE

    ne_type = models.CharField(max_length=64, choices=INSTANCE, null=True, blank=True)
    frequency_distribution = models.BigIntegerField(
        default=0
    )  # usage frequency in parsed text

    data_sources = models.ManyToManyField("DataSource", blank=True)
    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return "{} ({})".format(self.text, self.ne_type)


class WordCollection(models.Model):
    """
    n-grams, Collocations, Multi-Words, etc
    TODO: Common Contexts, Dispersion plot, Plotting the Frequency Distribution
    TODO: Add concept collections and tag(pos) collections
    """

    words = ArrayField(models.BigIntegerField(), blank=False, default=list, size=2)

    from datacore.components import WORD_COLLECTION

    collection_type = models.CharField(
        max_length=64, choices=WORD_COLLECTION, default="NGRAM"
    )


"""
Ontology's informal descriptors
describe ontology in natural language.
"""


class Example(models.Model):
    """
    Example of Lemmas.
    """

    text = models.TextField(null=True, unique=False)
    word = models.ForeignKey(Word, on_delete=models.CASCADE, null=True, blank=True)

    data_sources = models.ManyToManyField("DataSource", blank=True)
    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )


# TODO: add it with empty db
# class Meta:
#     unique_together = (("text", "language"),)


class Definition(models.Model):
    """
    Natural language definitions of concepts.
    """

    text = models.TextField(null=True, unique=False)

    data_sources = models.ManyToManyField("DataSource", blank=True)
    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )

    # TODO: add it with empty db
    # class Meta:
    #     unique_together = (("text", "language"),)

    def __str__(self):
        return self.text


"""
Ontology Learning Modes:
an ontology describs formal specification of a concept, class, set, or collection and relations and properties that connects it with others.
"""


class Concept(models.Model):
    """
    Also called: class, set, collection, object type, or a kind of thing(object, instance, literal, named entity).
    A concept is defined as a single cognitive entity(anything you can think of and describe) which describes parts of the world.
    concepts can be informally described using their synonyms, definition, examples, etc.
    concepts can be formally described using their relations, attributes, restrictions and attributes.
    """

    from datacore.components import POS

    pos = models.CharField(
        max_length=64, choices=POS, null=True, blank=True, verbose_name="Part of Speech"
    )

    synonyms = models.ManyToManyField(Word, related_name="lemma_synonym")
    antonyms = models.ManyToManyField(Word, related_name="lemma_antonym")
    definitions = models.ManyToManyField(Definition, related_name="concept_definition")
    examples = models.ManyToManyField(Example, related_name="concept_examples")

    ontology_domain = models.ForeignKey(
        "DomainOntology", on_delete=models.SET_NULL, null=True, blank=True
    )
    """
    Each concept can have it's own domain which is often used in Upper Ontology.
    Ontology Domains are considered domains of discource(a formal discussion or analysis of a specific subject).
    E.g. Biology, Computer Science
    """

    axiom = models.ForeignKey("Axiom", on_delete=models.SET_NULL, null=True, blank=True)
    """
    Axioms are theorems on relations.
    axioms for asserting facts about concepts, roles and instances.
    """

    usage_count = models.BigIntegerField(default=0)  # usage frequency in parsed text

    source_offset = models.BigIntegerField(null=True, unique=False)
    data_sources = models.ManyToManyField("DataSource", blank=True)
    data = JSONField(default=dict)
    """
    data is used to store extra detail about class such as:
    * it's unique ids in other data sources E.G., wordnet offset
    """

    def __str__(self):
        definitions = ""  # TODO: "{}".format(" ,".join([d.text for d in Definition.objects.filter(concept=self)]))
        return "{}: {}\n".format(
            " ,".join([synonym.text for synonym in self.synonyms.all()]), definitions
        )

    def get_title(self):
        return " ,".join([synonym.text for synonym in self.synonyms.all()])

    # TODO: remove since no longer used, definition and example are m2m now
    def get_definitions(self):
        definitions = Definition.objects.filter(concept=self)
        return definitions

    def get_examples(self):
        examples = Example.objects.filter(concept=self)
        return examples

    def function_terms(self):
        """
        # TODO: add this code
        Ontology Function Terms: Complex structures formed from certain relations that can be used in place of an instance term in a statement.
        """
        pass


class DomainOntology(MPTTModel):
    """
    Custome ontology domains, defined by user, and used for Lower Ontologies.
    for Upper Ontology(I.e. General language or common across all domains) it's possible to define a domain or add ontologies whithout domain.
    """

    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(default="")
    # parent of a "DomainOntology" maps domain of concept in Lower Ontology. E.g. Art < Drawing < Painting
    parent = TreeForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    # ontology type
    ONTOLOGY_CHOICES = (
        (1, "Upper Ontology"),
        (2, "Domain Ontology"),
    )
    ontology_domain = models.IntegerField(choices=ONTOLOGY_CHOICES, default=1)

    def __str__(self):
        return self.title


class Attribute(models.Model):
    """
    aspects, properties, features, characteristics, or parameters that a single object (or class) can have.
    They are defined based on usecases by knowledge expert. E.G., hasChild, hasAge
    We use Property model to describe an attribute and Attribute model holds the value for each attribute of a class
    """

    property = models.ForeignKey(
        "Property", blank=True, null=True, on_delete=models.CASCADE
    )
    """
    properties describe attribute. E.G., hasChild, isColored,
    """
    values = JSONField(default=dict)
    """
    TODO: use TextField for value and add ranges and value types to components and use two fields to point to them
    example: Ontology with class(synnonym:apple) has attribute(value:red) with property(title:color)
    structure example, pointing to a class(Object Property):
    {
        'value': '123'
        'type': 'class'
    }
    where 123 is the id of class.
    or value(DataType Property):
    {
        'value': 1999/9/9
        'type': 'datetype'
    }
    """


class Property(models.Model):
    """
    Properties(and Roles) are a collection of relationships between instances
    OWL properties are also called roles.
    """

    title = models.CharField(max_length=1024, null=False, blank=False)
    description = models.TextField()
    expression = models.CharField(
        max_length=1,
        choices=(
            ("a", "Adjective"),
            ("n", "Noun"),
        ),
        default="n",
    )
    """
    Each propery is expressed as an adjective or noun. E.G., apple's color is adjective, Joe's father is Poe.
    """
    # TODO: data_type = component.datatypes ~~~ can point to an ontology class to show it's a data object
    parent = TreeForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    """
    Propertie can be nested, this is for ease of use by knowledge experts:
    <hasChild,type,familyProperty>
    <hasDaughter,subPropertyOf,hasChild>
    <hasSon,subPropertyOf,hasChild>
    """


# restrictions = models.ManyToManyField("Restriction")


class Relation(models.Model):
    """
    ways in which classes and instances can be related to one another.
    Relations are limited to specified types which directly connects two ontology classes(or a concept to a class).
    """

    from datacore.components import RELATION

    concepts = ArrayField(models.BigIntegerField(), blank=False, default=list, size=2)
    relation_type = models.CharField(
        max_length=64, choices=RELATION, null=True, blank=True
    )
    ontology_domain = models.ForeignKey(
        "DomainOntology", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        s_concept = Concept.objects.get(id=self.concepts[0])
        t_concept = Concept.objects.get(id=self.concepts[1])
        return f"({s_concept.get_title()}) {self.get_relation_type_display()} ({t_concept.get_title()})"


class Rule(models.Model):
    """
    statements in the form of an if-then (antecedent-consequent) sentence that describe the logical inferences that can be drawn from an assertion in a particular form. Used for computation.
    a rule could be any statement which says that a certain conclusion must be valid whenever a certain premise is satisfied.
    I.E. Descriptive Logic, Inference
    E.G. if X is Y's father, then Y is X's child.
    """

    title = models.CharField(max_length=1024, null=False, blank=False)
    statements = JSONField(default=dict)
    ontology_domain = models.ForeignKey(
        "DomainOntology", on_delete=models.SET_NULL, null=True, blank=True
    )


class Restriction(models.Model):
    """
    formally stated descriptions of what must be true in order for some assertion to be accepted as input.
    """

    title = models.CharField(max_length=1024, null=False, blank=False)
    statements = JSONField(default=dict)
    ontology_domain = models.ForeignKey(
        "DomainOntology", on_delete=models.SET_NULL, null=True, blank=True
    )


class Axiom(models.Model):
    """
    Each axiom is a set of simple statements, assertions, and rules in formal language which are used in reasoning.
    An axiom can be more-general classes, restrictions, sets of instances, and boolean combinations of descriptions.
    """

    attributes = models.ManyToManyField("Attribute")
    ontology_domain = models.ForeignKey(
        "DomainOntology", on_delete=models.SET_NULL, null=True, blank=True
    )


class Event(models.Model):
    """
    the changing of attributes or relations.
    E.G., an instance(class:Woman) trigered Action("givingBirth"). now she should have the attribute "isMother".
    """

    pass


class Action(models.Model):
    """
    Actions are types of events which when trigered can call events.
    """

    pass


class Corpora(models.Model):
    """
    A collection of documents
    TODO: Refactor name to use corpus
    """

    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, unique=False)
    documents = models.ManyToManyField("Document")
    phrase_collections = models.ManyToManyField("PhraseCollection")
    data_sources = models.ManyToManyField("DataSource", blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("datacore:corpus", kwargs={"id": str(self.id)})


class PhraseCollection(models.Model):
    """
    A collection of phrases. it used to bind phrases to documents for purposes such as Q&A, Fact Checking, ...
    for example Squad dataset can have a 'Corpora', each of it's documents can be added as a 'Document' to the corpora and it's questions for that document can be added to a 'PhraseCollection' and itself to 'Document.phrase_collections'
    """

    title = models.CharField(max_length=1024, null=True, blank=True)
    description = models.TextField(null=True, blank=True, unique=False)
    phrases = models.ManyToManyField("Phrase")
    data_sources = models.ManyToManyField("DataSource", blank=True)

    def __str__(self):
        return self.title


class Document(models.Model):
    title = models.TextField(null=True, unique=False)
    content = models.TextField(null=False, unique=False, default="")
    raw_content = models.TextField(
        null=True, blank=True, unique=False
    )  # raw content for unprocessed sources such as html, rtf...
    phrases = models.ManyToManyField("Phrase", related_name="document_phrase")
    phrase_collections = models.ManyToManyField("PhraseCollection")
    topic = models.TextField(null=True, blank=True, unique=False)
    # TODO: add type: plain text, titled text, chaptered text, html, markup

    data_sources = models.ManyToManyField("DataSource", blank=True)
    language = models.ForeignKey(
        "datacore.Language", on_delete=models.CASCADE, blank=True, null=True
    )

    def __str__(self):
        if self.title:
            return self.title
        else:
            return f"DOCUMENT: {self.content[0:100]}..."


class PhraseRelationType(models.Model):
    """
    Relation types between phrases, E.g. translations, paraphrases, answers
    """

    title = models.CharField(max_length=2048, unique=True)
    description = models.TextField(default="")

    def __str__(self):
        return self.title


class PhraseRelations(models.Model):
    """
    Stores phrase relations,
    for example: two or more phrases can be selected in `phrases` field. with the `phrase_relation` set to paraphrase, and `data` field holding it's meta-data such as level of formality, usage region, or it's domain.
    """

    phrases = models.ManyToManyField("Phrase", related_name="related_phrase")
    phrase_relation = models.ForeignKey(
        "PhraseRelationType", on_delete=models.SET_NULL, blank=True, null=True
    )
    data = JSONField(default=dict)


class PhraseAnalysis(models.Model):
    """
    Stores analysis recored of a phrase.
    """

    phrase = models.ForeignKey(
        "Phrase", on_delete=models.CASCADE, null=False, blank=False
    )
    analyzer = models.ForeignKey(
        "Analyzer", on_delete=models.CASCADE, null=True, blank=True
    )  # TODO: , null=False, blank=False
    """
    analyzer can be specific NLP framework or a user with this string format: <user:USER_ID>
    """
    sentiment = models.FloatField(
        default=0, validators=[MaxValueValidator(1.0), MinValueValidator(-1.0)]
    )
    # TODO: add intent
    # Removed: phrase_type = models.ForeignKey("Component", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={"pk__in":Component.objects.get(code="PHRASE").get_descendants(include_self=False).values('pk')})
    from datacore.components import PHRASE

    phrase_type = models.CharField(max_length=64, choices=PHRASE, null=True, blank=True)
    words = models.ManyToManyField("Word")  # tokenized words
    entities = models.ManyToManyField("NamedEntity", related_name="used_ne")
    template = models.ForeignKey(
        "Template",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="phrase_template",
    )

    data = JSONField(default=dict)
    """
    data is used to store analysis data in json format.
    """

    def __str__(self):
        return "({}) {}".format(self.analyzer.title, self.phrase.text)

    class Meta:
        unique_together = (("phrase", "analyzer"),)


class Phrase(models.Model):
    """
    Stores a phrase or sentence.
    Phrases should not be unique as a phrase can have different analysis based on document content
    """

    # If it doesn't have a document, it should be unique
    text = models.TextField(null=False, unique=False, default="")
    # TODO: use ids instead of text
    words_list = ArrayField(models.CharField(max_length=2048), blank=True, default=list)
    lemmas_list = ArrayField(
        models.CharField(max_length=2048), blank=True, default=list
    )
    entities_list = ArrayField(
        models.CharField(max_length=2048), blank=True, default=list
    )

    data_sources = models.ManyToManyField("DataSource", blank=True)
    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )

    data = JSONField(default=dict)

    def __str__(self):
        return self.text

    class Meta:
        unique_together = (("text", "language"),)


class Template(MPTTModel):
    """
    Phrase and sentence template
    Each template can be treated as a base template, a sub-template with child-template
    Base Template:
            parent=None
            This template is for simplest form of a phrase
    sub-template:
            parent!=None
            A branch of base template structure with syntactical differences.
    child-template:
            parent!=None
            A refference from a wrongly taged(bacause of typo, dialects, or bad analysis)
    Axioms and rules in regard to sub-templates and child templates are stored in 'data'

    """

    title = models.CharField(max_length=1024, null=True, blank=True)
    pos = models.TextField(null=False, blank=False)
    """
    only Part of Speach tags.
    """
    xpos = models.TextField(null=True, blank=True)
    """
    treebank-specific POS which exists for some languages, also called Fine-grained part-of-speech.
    """
    feats = models.TextField(null=True, blank=True)
    """
    universal morphological features: https://universaldependencies.org/u/feat/index.html
    """
    constituency = models.TextField(null=True, blank=True)
    """
    Constituency parsing template
    """

    dep = models.TextField(null=True, blank=True)
    """
    dependency template.
    format:
    (wordID,wordPOS,depRelation,depID)-(...)-...
    example:
    (1,PROPN,compound,2)-(2,PROPN,nsubj,4)-(3,AUX,cop,4)-(4,ADV,root,0)-(5,ADP,case,6)-(6,PROPN,obl,4)-(7,PUNCT,punct,4)
    """
    from datacore.components import PHRASE

    phrase_type = models.CharField(max_length=64, choices=PHRASE, null=True, blank=True)

    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="t_children",
    )  # for sub-templates
    """
    indicates a sub-template or child-template
    """
    data = JSONField(default=dict, blank=True)
    """
    general structure of template and specifications about rules and axioms regarding parent
    """
    language = models.ForeignKey(
        "Language", on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ("pos", "language")

    # causes: ERROR: index row size [NUMBER] exceeds maximum [NUMBER] for index "index_oauth_access_tokens_on_token" HINT: Values larger than [NUMBER]/[NUMBER] of a buffer page cannot be indexed. Consider a function index of an MD5 hash of the value, or use full text indexing.

    def phrase_count(self):
        analysis = PhraseAnalysis.objects.filter(template=self)
        phrases = []
        for item in analysis:
            phrases.append(item.phrase.id) if item.phrase.id not in phrases else None
        return len(phrases)

    def __str__(self):
        if self.title:
            return "{}: {}".format(self.text, self.pos)
        else:
            return self.pos

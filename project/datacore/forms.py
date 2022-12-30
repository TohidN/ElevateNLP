from datacore.models import (
    Component,
    Concept,
    Corpora,
    DataSource,
    Definition,
    Document,
    DomainOntology,
    Example,
    Language,
    NamedEntity,
    Phrase,
    PhraseCollection,
    Reference,
    Relation,
    Word,
    WordList,
    WordRelation,
    WordRelationType,
)
from django import forms
from mptt.forms import TreeNodeChoiceField


class CorpusForm(forms.ModelForm):
    title = forms.CharField(
        max_length=1024, required=True, help_text="Please enter a valid Corpus name."
    )
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A corpus can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Corpora
        fields = ["title", "description", "data_sources"]


class DocumentForm(forms.ModelForm):
    title = forms.CharField(
        max_length=1024, required=False, help_text="Please enter a valid Document name."
    )
    content = forms.CharField(
        required=True, widget=forms.Textarea(attrs={"rows": "12"})
    )
    raw_content = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "12"})
    )
    topic = forms.CharField(
        max_length=1024, required=False, help_text="Please enter a valid topic."
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Document can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

    class Meta:
        model = Document
        fields = [
            "title",
            "content",
            "raw_content",
            "topic",
            "data_sources",
            "language",
        ]


class PhraseCollectionForm(forms.ModelForm):
    title = forms.CharField(
        max_length=1024,
        required=False,
        help_text="Please enter a valid Collection name.",
    )
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Collection can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = PhraseCollection
        fields = ["title", "description", "data_sources"]


class PhraseForm(forms.ModelForm):
    text = forms.CharField(
        max_length=1024, required=False, help_text="Please enter a valid Phrase."
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Phrase can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

    class Meta:
        model = Phrase
        fields = ["text", "data_sources", "language"]


class WordForm(forms.ModelForm):
    text = forms.CharField(
        max_length=64, required=False, help_text="Please enter a valid Word."
    )
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

    class Meta:
        model = Word
        fields = ["text", "language"]


class WordsFilter(forms.Form):
    SORT_TYPE = (
        ("asc", "Ascending"),
        ("dsc", "Descending"),
    )
    SORT_BY = (
        ("wrd_txt", "Alphabetical"),
        ("wrd_len", "Word Length"),
        ("wrd_frq", "Word Usage Frequency"),
        ("lma_frq", "Lemma Usage Frequency"),
    )
    start = forms.CharField(
        max_length=256,
        required=False,
        help_text="Words must start with this characters",
    )
    contain = forms.CharField(
        max_length=256, required=False, help_text="Words must contain this characters"
    )
    end = forms.CharField(
        max_length=256, required=False, help_text="Words must end with this characters"
    )
    sort_by = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=SORT_BY,
        initial="",
        label="Sort Type",
        required=False,
    )
    sort_type = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=SORT_TYPE,
        initial="",
        label="Sort By",
        required=False,
    )


class DomainOntologyForm(forms.ModelForm):
    title = forms.CharField(
        max_length=1024, required=True, help_text="Please enter a valid Ontology name."
    )
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )
    parent = TreeNodeChoiceField(queryset=DomainOntology.objects.all(), required=False)
    ontology_domain = forms.ChoiceField(
        choices=DomainOntology.ONTOLOGY_CHOICES, required=False
    )

    class Meta:
        model = DomainOntology
        fields = ["title", "description", "parent", "ontology_domain"]


class ConceptForm(forms.ModelForm):
    obj_pos = Component.objects.get(slug="pos")
    pos = TreeNodeChoiceField(
        queryset=obj_pos.get_descendants(),
        start_level=obj_pos.level,
        to_field_name="code",
        label="Part of Speech",
        required=True,
    )
    ontology_domain = forms.ModelChoiceField(
        queryset=DomainOntology.objects.all(), required=False
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Concept can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )

    def clean(self):
        # in default clean function <Component> object is sent. this method override sends string instead of object.
        self.cleaned_data["pos"] = self.data["pos"]
        return super(ConceptForm, self).clean()

    class Meta:
        model = Concept
        fields = ["pos", "ontology_domain", "data_sources"]


class DefinitionForm(forms.ModelForm):
    text = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": "3"}))
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Definition can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Definition
        fields = ["text", "language", "data_sources"]


class ExampleForm(forms.ModelForm):
    text = forms.CharField(required=True, widget=forms.Textarea(attrs={"rows": "3"}))
    # TODO: define new field type which allows search and select
    word = forms.ModelChoiceField(queryset=Word.objects.all(), required=True)
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Definition can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Example
        fields = ["text", "word", "language", "data_sources"]

    def parent_initialize(self, parent=None):
        # it limits word field options to concept's synonyms or antonyms
        # parent: a concept.
        self.fields["word"].queryset = parent.synonyms.all()  # | parent.antonyms.all()


class RelationForm(forms.ModelForm):
    from datacore.components import RELATION
    from django.contrib.postgres.forms import SplitArrayField

    concepts = SplitArrayField(
        forms.IntegerField(), size=2, required=True, help_text="Enter two concept IDs."
    )
    relation_type = forms.ChoiceField(choices=RELATION, required=True)

    class Meta:
        model = Relation
        fields = ["concepts", "relation_type"]


class NamedEntityForm(forms.ModelForm):
    text = forms.CharField(max_length=2048, required=True)
    parent = TreeNodeChoiceField(queryset=NamedEntity.objects.all(), required=False)
    obj_instance = Component.objects.get(slug="onto/instance")
    ne_type = TreeNodeChoiceField(
        queryset=obj_instance.get_descendants(),
        start_level=obj_instance.level + 1,
        to_field_name="code",
        label="Entity Type",
        required=False,
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        help_text="A Named Entity can have one or more data sources.",
        widget=forms.CheckboxSelectMultiple,
    )
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

    def clean(self):
        # self.cleaned_data['parent'] = self.data['parent']
        self.cleaned_data["ne_type"] = self.data["ne_type"]
        return super(NamedEntityForm, self).clean()

    class Meta:
        model = NamedEntity
        fields = ["text", "parent", "ne_type", "data_sources", "language"]


class LanguageForm(forms.ModelForm):
    native_name = forms.CharField(max_length=256, required=True)
    en_name = forms.CharField(max_length=256, required=True)
    native_speakers = forms.IntegerField(required=False)
    alpha2 = forms.CharField(max_length=2, required=False)
    alpha3b = forms.CharField(max_length=3, required=True)
    alpha3t = forms.CharField(max_length=3, required=False)

    class Meta:
        model = Language
        fields = [
            "native_name",
            "en_name",
            "native_speakers",
            "alpha2",
            "alpha3b",
            "alpha3t",
        ]


class WordRelationTypeForm(forms.ModelForm):
    title = forms.CharField(max_length=2048, required=True)
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )
    direction_type = forms.ChoiceField(
        choices=WordRelationType.DIRECTIONS, required=True
    )
    descriptor = forms.CharField(max_length=2048, required=True)
    reverse_descriptor = forms.CharField(max_length=2048, required=False)

    class Meta:
        model = WordRelationType
        fields = [
            "title",
            "description",
            "direction_type",
            "descriptor",
            "reverse_descriptor",
        ]


class WordRelationForm(forms.Form):
    word_one = forms.CharField(max_length=64, required=True, label="Word")
    word_one_language = forms.ModelChoiceField(
        queryset=Language.objects.all(), required=False
    )
    word_relation = forms.ModelChoiceField(
        queryset=WordRelationType.objects.all(), required=True
    )
    word_two = forms.CharField(max_length=64, required=True, label="Word")
    word_two_language = forms.ModelChoiceField(
        queryset=Language.objects.all(), required=False
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )


class WordRelationEditForm(forms.ModelForm):
    word_relation = forms.ModelChoiceField(
        queryset=WordRelationType.objects.all(), required=True
    )
    data_sources = forms.ModelMultipleChoiceField(
        queryset=DataSource.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = WordRelation
        fields = ["word_relation", "data_sources"]


class WordListForm(forms.ModelForm):
    title = forms.CharField(max_length=2048, required=True)
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )

    class Meta:
        model = WordList
        fields = ["title", "description"]


class DataSourceForm(forms.ModelForm):
    title = forms.CharField(max_length=256, required=True)
    version = forms.CharField(max_length=256, required=False)
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )

    class Meta:
        model = DataSource
        fields = ["title", "description", "version"]


class ReferenceForm(forms.ModelForm):
    title = forms.CharField(max_length=256, required=True)
    url = forms.URLField(required=False)
    description = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": "3"})
    )

    class Meta:
        model = Reference
        fields = ["title", "url", "description"]


class LexicalExportForm(WordsFilter):
    limit = forms.IntegerField(
        required=False,
        label="Limit to top results",
        help_text="Leave empty to list all items.",
    )


class TextualExportForm(forms.Form):
    IMPORT_TYPE = (
        ("cor", "All Corpora"),
        ("doc", "All Documents"),
        ("phr", "All Phrases"),
    )
    import_type = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=IMPORT_TYPE,
        initial="",
        label="Import",
        required=True,
    )


class DomainOntologyExportForm(forms.Form):
    domain_ontology = forms.ModelChoiceField(
        required=True, queryset=DomainOntology.objects.all()
    )
    language = forms.ModelChoiceField(queryset=Language.objects.all(), required=False)

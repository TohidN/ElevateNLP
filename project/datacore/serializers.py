from rest_framework import serializers

from . import models


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DataSource
        fields = "__all__"


class ReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reference
        fields = "__all__"


class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Component
        fields = [
            "id",
            "title",
            "description",
            "parent",
            "slug",
            "code",
            "codes",
            "component_type",
            "references",
            "data",
        ]


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = "__all__"


class WordRelationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WordRelationType
        fields = "__all__"


class WordRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WordRelation
        fields = "__all__"


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Word
        fields = "__all__"


class NamedEntitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NamedEntity
        fields = "__all__"


class WordCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.WordCollection
        fields = "__all__"


class ConceptSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Concept
        fields = "__all__"


class DomainOntologySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DomainOntology
        fields =  [
            "id",
            "title",
            "description",
            "ontology_domain",
            "parent",
        ]


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Definition
        fields = "__all__"


class ExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Example
        fields = "__all__"


class RelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Relation
        fields = "__all__"


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Property
        fields = "__all__"


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rule
        fields = "__all__"


class RestrictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Restriction
        fields = "__all__"


class AxiomSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Axiom
        fields = "__all__"


class CorporaSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Corpora
        fields = "__all__"


class PhraseCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhraseCollection
        fields = "__all__"


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Document
        fields = "__all__"


class PhraseRelationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PhraseRelationType
        fields = "__all__"


class PhraseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Phrase
        fields = "__all__"


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Template
        fields = "__all__"

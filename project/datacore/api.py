from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers


class DataSourceViewSet(viewsets.ModelViewSet):
    queryset = models.DataSource.objects.all()
    serializer_class = serializers.DataSourceSerializer


class ReferenceViewSet(viewsets.ModelViewSet):
    queryset = models.Reference.objects.all()
    serializer_class = serializers.ReferenceSerializer


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = models.Component.objects.all()
    serializer_class = serializers.ComponentSerializer


class LanguageViewSet(viewsets.ModelViewSet):
    queryset = models.Language.objects.all()
    serializer_class = serializers.LanguageSerializer


class WordRelationTypeViewSet(viewsets.ModelViewSet):
    queryset = models.WordRelationType.objects.all()
    serializer_class = serializers.WordRelationTypeSerializer


class WordRelationViewSet(viewsets.ModelViewSet):
    queryset = models.WordRelation.objects.all()
    serializer_class = serializers.WordRelationSerializer


class NamedEntityViewSet(viewsets.ModelViewSet):
    queryset = models.NamedEntity.objects.all()
    serializer_class = serializers.NamedEntitySerializer


class WordCollectionViewSet(viewsets.ModelViewSet):
    queryset = models.WordCollection.objects.all()
    serializer_class = serializers.WordCollectionSerializer


class WordViewSet(viewsets.ModelViewSet):
    Word = models.Word
    queryset = Word.objects.all()
    serializer_class = serializers.WordSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = [
        "id",
        "text",
        "frequency_distribution",
        "lemma_frequency_distribution",
        "language",
    ]
    search_fields = ["text"]

    @action(detail=False)
    def longest(self, request):
        queryset = models.Word.filter_words(sort_by="wrd_len", sort_type="dsc")
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # TODO: min/max lengh, letters(contains letters/must have/ can't have)
    @action(detail=False)
    def filter(self, request):
        # api/words/filter/?ends_with=ed&starts_with=non&contains=tut
        # api/words/filter/?list-type=longest
        queryset = models.Word.objects
        list_type = self.request.query_params.get("list-type")
        if list_type == "longest":
            queryset = models.Word.filter_words(sort_by="wrd_len", sort_type="dsc")
        else:
            starts_with = self.request.query_params.get("starts_with")
            ends_with = self.request.query_params.get("ends_with")
            contains = self.request.query_params.get("contains")
            queryset = models.Word.filter_words(
                start=starts_with, contain=contains, end=ends_with
            )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class ConceptViewSet(viewsets.ModelViewSet):
    queryset = models.Concept.objects.all()
    serializer_class = serializers.ConceptSerializer


class DomainOntologyViewSet(viewsets.ModelViewSet):
    queryset = models.DomainOntology.objects.all()
    serializer_class = serializers.DomainOntologySerializer


class DefinitionViewSet(viewsets.ModelViewSet):
    queryset = models.Definition.objects.all()
    serializer_class = serializers.DefinitionSerializer


class ExampleViewSet(viewsets.ModelViewSet):
    queryset = models.Example.objects.all()
    serializer_class = serializers.ExampleSerializer


class RelationViewSet(viewsets.ModelViewSet):
    queryset = models.Relation.objects.all()
    serializer_class = serializers.RelationSerializer


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = models.Attribute.objects.all()
    serializer_class = serializers.AttributeSerializer


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = models.Property.objects.all()
    serializer_class = serializers.PropertySerializer


class RuleViewSet(viewsets.ModelViewSet):
    queryset = models.Rule.objects.all()
    serializer_class = serializers.RuleSerializer


class RestrictionViewSet(viewsets.ModelViewSet):
    queryset = models.Restriction.objects.all()
    serializer_class = serializers.RestrictionSerializer


class AxiomViewSet(viewsets.ModelViewSet):
    queryset = models.Axiom.objects.all()
    serializer_class = serializers.AxiomSerializer


class CorporaViewSet(viewsets.ModelViewSet):
    queryset = models.Corpora.objects.all()
    serializer_class = serializers.CorporaSerializer


class PhraseCollectionViewSet(viewsets.ModelViewSet):
    queryset = models.PhraseCollection.objects.all()
    serializer_class = serializers.PhraseCollectionSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = models.Document.objects.all()
    serializer_class = serializers.DocumentSerializer


class PhraseRelationTypeViewSet(viewsets.ModelViewSet):
    queryset = models.PhraseRelationType.objects.all()
    serializer_class = serializers.PhraseRelationTypeSerializer


class PhraseViewSet(viewsets.ModelViewSet):
    queryset = models.Phrase.objects.all()
    serializer_class = serializers.PhraseSerializer


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = models.Template.objects.all()
    serializer_class = serializers.TemplateSerializer

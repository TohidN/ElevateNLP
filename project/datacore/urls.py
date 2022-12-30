from django.conf.urls import include
from django.urls import path, re_path
from rest_framework import routers

from . import api, views

app_name = "datacore"

router = routers.DefaultRouter()
router.register(r"data_sources", api.DataSourceViewSet)
router.register(r"references", api.ReferenceViewSet)
router.register(r"linguistics", api.ComponentViewSet)
router.register(r"languages", api.LanguageViewSet)
router.register(r"word_relation_types", api.WordRelationTypeViewSet)
router.register(r"word_relation", api.WordRelationViewSet)
router.register(r"words", api.WordViewSet)
router.register(r"named_entities", api.NamedEntityViewSet)
router.register(r"word_collections", api.WordCollectionViewSet)
router.register(r"concepts", api.ConceptViewSet)
router.register(r"domain_ontologies", api.DomainOntologyViewSet)
router.register(r"definitions", api.DefinitionViewSet)
router.register(r"examples", api.ExampleViewSet)
router.register(r"relations", api.RelationViewSet)
router.register(r"attributes", api.AttributeViewSet)
router.register(r"properties", api.PropertyViewSet)
router.register(r"rules", api.RuleViewSet)
router.register(r"restrictions", api.RestrictionViewSet)
router.register(r"axioms", api.AxiomViewSet)
router.register(r"corpus", api.CorporaViewSet)
router.register(r"phrase_collection", api.PhraseCollectionViewSet)
router.register(r"documents", api.DocumentViewSet)
router.register(r"phrase_relation_types", api.PhraseRelationTypeViewSet)
router.register(r"phrases", api.PhraseViewSet)
router.register(r"templates", api.TemplateViewSet)


urlpatterns = [
    # home
    re_path(r"^$", views.index, name="home"),
    path("search/", views.search, name="search"),
    path("analyze/", views.analyze, name="analyze"),
    # API
    path(r"api/", include((router.urls, "datacore"))),
    # all the pages
    path("corpora/", views.corpora, name="corpora"),
    path("corpora/add/", views.corpora_add, name="corpora_add"),
    re_path(
        r"^corpus/(?P<id>\d+)/documents_add$",
        views.corpus_documents_add,
        name="corpus_documents_add",
    ),
    re_path(
        r"^corpus/(?P<id>\d+)/documents$",
        views.corpus_documents,
        name="corpus_documents",
    ),
    re_path(
        r"^corpus/(?P<id>\d+)/phrase_collections_add$",
        views.corpus_phrase_collections_add,
        name="corpus_phrase_collections_add",
    ),
    re_path(
        r"^corpus/(?P<id>\d+)/phrase_collections$",
        views.corpus_phrase_collections,
        name="corpus_phrase_collections",
    ),
    re_path(r"^corpus/(?P<id>\d+)/edit$", views.corpus_edit, name="corpus_edit"),
    re_path(r"^corpus/(?P<id>\d+)/delete$", views.corpus_delete, name="corpus_delete"),
    re_path(r"^corpus/(?P<id>\d+)/$", views.corpus, name="corpus"),
    path("documents/", views.documents, name="documents"),
    path("documents/add", views.documents_add, name="documents_add"),
    re_path(r"^document/(?P<id>\d+)/edit$", views.document_edit, name="document_edit"),
    re_path(
        r"^document/(?P<id>\d+)/delete$", views.document_delete, name="document_delete"
    ),
    re_path(r"^document/(?P<id>\d+)$", views.document, name="document"),
    path("phrase-collections/", views.phrase_collections, name="phrase_collections"),
    path(
        "phrase-collections/add",
        views.phrase_collections_add,
        name="phrase_collections_add",
    ),
    re_path(
        r"^phrase-collection/(?P<id>\d+)/add_phrase$",
        views.phrase_collection_add_phrase,
        name="phrase_collection_add_phrase",
    ),
    re_path(
        r"^phrase-collection/(?P<id>\d+)/edit$",
        views.phrase_collection_edit,
        name="phrase_collection_edit",
    ),
    re_path(
        r"^phrase-collection/(?P<id>\d+)/delete$",
        views.phrase_collection_delete,
        name="phrase_collection_delete",
    ),
    re_path(
        r"^phrase-collection/(?P<id>\d+)$",
        views.phrase_collection,
        name="phrase_collection",
    ),
    path("phrases/", views.phrases, name="phrases"),
    path("phrases/add", views.phrases_add, name="phrases_add"),
    re_path(r"^phrase/(?P<id>\d+)/edit$", views.phrase_edit, name="phrase_edit"),
    re_path(r"^phrase/(?P<id>\d+)/delete$", views.phrase_delete, name="phrase_delete"),
    re_path(r"^phrase/(?P<id>\d+)$", views.phrase, name="phrase"),
    path("words/", views.words, name="words"),
    path("words/add", views.words_add, name="words_add"),
    re_path(r"^word/(?P<id>\d+)/edit$", views.word_edit, name="word_edit"),
    re_path(r"^word/(?P<id>\d+)/delete$", views.word_delete, name="word_delete"),
    re_path(r"^word/(?P<id>\d+)$", views.word, name="word"),
    path("domain_ontologies/", views.domain_ontologies, name="domain_ontologies"),
    path(
        "domain_ontologies/add",
        views.domain_ontologies_add,
        name="domain_ontologies_add",
    ),
    re_path(
        r"^domain_ontology/(?P<id>\d+)/concept_add$",
        views.domain_ontology_concept_add,
        name="domain_ontology_concept_add",
    ),
    re_path(
        r"^domain_ontology/(?P<id>\d+)/edit$",
        views.domain_ontology_edit,
        name="domain_ontology_edit",
    ),
    re_path(
        r"^domain_ontology/(?P<id>\d+)/delete$",
        views.domain_ontology_delete,
        name="domain_ontology_delete",
    ),
    re_path(
        r"^domain_ontology/(?P<id>\d+)$", views.domain_ontology, name="domain_ontology"
    ),
    path("concepts/", views.concepts, name="concepts"),
    path("concepts/add", views.concepts_add, name="concepts_add"),
    re_path(
        r"^concept/(?P<id>\d+)/synonyms$",
        views.concept_synonyms,
        name="concept_synonyms",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/synonyms_add$",
        views.concept_synonyms_add,
        name="concept_synonyms_add",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/synonym_edit/(?P<rel_id>\d+)$",
        views.concept_synonym_edit,
        name="concept_synonym_edit",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/antonyms$",
        views.concept_antonyms,
        name="concept_antonyms",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/antonyms_add$",
        views.concept_antonyms_add,
        name="concept_antonyms_add",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/antonym_edit/(?P<rel_id>\d+)$",
        views.concept_antonym_edit,
        name="concept_antonym_edit",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/definitions$",
        views.concept_definitions,
        name="concept_definitions",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/definitions_add$",
        views.concept_definitions_add,
        name="concept_definitions_add",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/definition_edit/(?P<rel_id>\d+)$",
        views.concept_definition_edit,
        name="concept_definition_edit",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/examples$",
        views.concept_examples,
        name="concept_examples",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/examples_add$",
        views.concept_examples_add,
        name="concept_examples_add",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/example_edit/(?P<rel_id>\d+)$",
        views.concept_example_edit,
        name="concept_example_edit",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/relationships$",
        views.concept_relationships,
        name="concept_relationships",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/relationships_add$",
        views.concept_relationships_add,
        name="concept_relationships_add",
    ),
    re_path(
        r"^concept/(?P<id>\d+)/visualization$",
        views.concept_visualization,
        name="concept_visualization",
    ),
    re_path(r"^concept/(?P<id>\d+)$", views.concept, name="concept"),
    path("entities/", views.entities, name="entities"),
    path("entities/add", views.entities_add, name="entities_add"),
    re_path(r"^entity/(?P<id>\d+)/edit$", views.entity_edit, name="entity_edit"),
    re_path(r"^entity/(?P<id>\d+)/delete$", views.entity_delete, name="entity_delete"),
    re_path(r"^entity/(?P<id>\d+)$", views.entity, name="entity"),
    path("templates/", views.templates, name="templates"),
    re_path(r"^template/(?P<id>\d+)$", views.template, name="template"),
    path("components/", views.components, name="components"),
    re_path(r"^component/(?P<slug>.+)/$", views.component, name="component"),
    path("languages/", views.languages, name="languages"),
    path("languages/add", views.languages_add, name="languages_add"),
    re_path(r"^language/(?P<id>\d+)/edit$", views.language_edit, name="language_edit"),
    re_path(
        r"^language/(?P<id>\d+)/delete$", views.language_delete, name="language_delete"
    ),
    re_path(r"^language/(?P<id>\d+)/$", views.language, name="language"),
    path("word-relation-types/", views.word_relation_types, name="word_relation_types"),
    path(
        "word-relation-types/add",
        views.word_relation_types_add,
        name="word_relation_types_add",
    ),
    re_path(
        r"^word-relation-type/(?P<id>\d+)/edit$",
        views.word_relation_type_edit,
        name="word_relation_type_edit",
    ),
    re_path(
        r"^word-relation-type/(?P<id>\d+)/delete$",
        views.word_relation_type_delete,
        name="word_relation_type_delete",
    ),
    re_path(
        r"^word-relation-type/(?P<id>\d+)$",
        views.word_relation_type,
        name="word_relation_type",
    ),
    path("word-relations/", views.word_relations, name="word_relations"),
    path("word-relations/add", views.word_relations_add, name="word_relations_add"),
    re_path(
        r"^word-relation/(?P<id>\d+)/edit$",
        views.word_relation_edit,
        name="word_relation_edit",
    ),
    re_path(
        r"^word-relation/(?P<id>\d+)/delete$",
        views.word_relation_delete,
        name="word_relation_delete",
    ),
    re_path(r"^word-relation/(?P<id>\d+)$", views.word_relation, name="word_relation"),
    path("word-lists/", views.word_lists, name="word_lists"),
    path("word-lists/add", views.word_lists_add, name="word_lists_add"),
    re_path(
        r"^word-list/(?P<id>\d+)/word_add$",
        views.word_list_word_add,
        name="word_list_word_add",
    ),
    re_path(
        r"^word-list/(?P<id>\d+)/edit$", views.word_list_edit, name="word_list_edit"
    ),
    re_path(
        r"^word-list/(?P<id>\d+)/delete$",
        views.word_list_delete,
        name="word_list_delete",
    ),
    re_path(r"^word-list/(?P<id>\d+)$", views.word_list, name="word_list"),
    path("data-sources/", views.data_sources, name="data_sources"),
    path("data-sources/add", views.data_sources_add, name="data_sources_add"),
    re_path(
        r"^data-source/(?P<id>\d+)/add_references$",
        views.data_source_add_references,
        name="data_source_add_references",
    ),
    re_path(
        r"^data-source/(?P<id>\d+)/edit$",
        views.data_source_edit,
        name="data_source_edit",
    ),
    re_path(
        r"^data-source/(?P<id>\d+)/delete$",
        views.data_source_delete,
        name="data_source_delete",
    ),
    re_path(r"^data-source/(?P<id>\d+)$", views.data_source, name="data_source"),
    path("datasets/lexical", views.lexical_data, name="lexical_data"),
    path(
        "datasets/lexical/export", views.lexical_data_export, name="lexical_data_export"
    ),
    path("datasets/textual", views.textual_data, name="textual_data"),
    path(
        "datasets/textual/export", views.textual_data_export, name="textual_data_export"
    ),
    path("datasets/ontological", views.ontological_data, name="ontological_data"),
    path(
        "datasets/ontological/export",
        views.ontological_data_export,
        name="ontological_data_export",
    ),
]

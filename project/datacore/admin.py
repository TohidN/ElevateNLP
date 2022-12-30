from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from . import models

# from django_summernote.admin import SummernoteModelAdmin


class AnalyzerAdmin(admin.ModelAdmin):
    search_fields = ["title", "version", "description"]


class DataSourceAdmin(admin.ModelAdmin):
    search_fields = ["title", "version"]
    ordering = [
        "title",
    ]


class ReferenceAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    ordering = [
        "title",
    ]


class ComponentAdmin(DraggableMPTTAdmin):  # , SummernoteModelAdmin
    # search_fields = ['title', 'description', 'code', 'codes__ucode', 'codes__wn']
    search_fields = ["code"]
    # summernote_fields = ('description', )


class LanguageAdmin(admin.ModelAdmin):
    search_fields = ["native_name", "en_name"]
    ordering = ("en_name",)


class RelationInline(admin.TabularInline):
    model = models.Relation


class ExampleInline(admin.StackedInline):
    model = models.Example


class DomainOntologyAdmin(admin.ModelAdmin):
    search_fields = ["title"]


class ConceptAdmin(admin.ModelAdmin):
    raw_id_fields = ("synonyms", "antonyms")
    # inlines = [DefinitionInline, ExampleInline]


class NamedEntityAdmin(admin.ModelAdmin):
    search_fields = ["text"]
    ordering = ("text",)


class WordRelationTypeAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    ordering = ("title",)


class WordRelationAdmin(admin.ModelAdmin):
    search_fields = ["words"]


class WordAdmin(admin.ModelAdmin):
    search_fields = ["text"]
    ordering = ("text",)


class WordListAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    ordering = ("title",)


class CorporaAdmin(admin.ModelAdmin):
    raw_id_fields = ("documents",)


class PhraseCollectionAdmin(admin.ModelAdmin):
    raw_id_fields = ("phrases",)


class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ("phrases",)


class PhraseAdmin(admin.ModelAdmin):
    pass


class TemplateAdmin(admin.ModelAdmin):
    search_fields = ["pos", "xpos", "feats"]


class PhraseAnalysis(admin.ModelAdmin):
    raw_id_fields = ("phrase", "words", "entities", "template")


admin.site.register(models.Analyzer, AnalyzerAdmin)
admin.site.register(models.DataSource, DataSourceAdmin)
admin.site.register(models.Reference, ReferenceAdmin)
admin.site.register(models.Component, ComponentAdmin)
admin.site.register(models.Language, LanguageAdmin)
admin.site.register(models.WordRelationType, WordRelationTypeAdmin)
admin.site.register(models.WordRelation, WordRelationAdmin)
admin.site.register(models.Word, WordAdmin)
admin.site.register(models.WordList, WordListAdmin)
admin.site.register(models.Definition)
admin.site.register(models.DomainOntology, DomainOntologyAdmin)
admin.site.register(models.Concept, ConceptAdmin)
admin.site.register(models.NamedEntity, NamedEntityAdmin)
admin.site.register(models.Relation)
admin.site.register(models.Corpora, CorporaAdmin)
admin.site.register(models.PhraseCollection, PhraseCollectionAdmin)
admin.site.register(models.Document, DocumentAdmin)
admin.site.register(models.Phrase, PhraseAdmin)
admin.site.register(models.PhraseAnalysis, PhraseAnalysis)
admin.site.register(models.Template, TemplateAdmin)

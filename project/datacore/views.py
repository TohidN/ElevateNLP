from datacore.functions.utils import prepare_pagination
from datacore.models import Concept, Document, Example, Phrase, Relation, Template, Word
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def index(request):
    context = {
        "concepts": Concept.objects.all().count(),
        "words": Word.objects.all().count(),
        "examples": Example.objects.all().count(),
        "phrases": Phrase.objects.all().count(),
        "documents": Document.objects.all().count(),
        "relationships": Relation.objects.all().count(),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "index.html", context)


def search(request):
    from datacore.models import Concept, Word

    query = request.GET.get("query")
    querytype = request.GET.get("type")
    if querytype == "phrase":
        try:
            phrases = Phrase.objects.filter(text__icontains=query)
        except Phrase.DoesNotExist:
            phrases = []
        context = {
            "type": querytype,
            "query": query,
            "phrases": phrases,
        }
    else:
        try:
            words = Word.objects.filter(text=query)
            concepts = Concept.objects.filter(synonyms__in=words)
        except Word.DoesNotExist or Concept.DoesNotExist:
            words = None
            concepts = []
        context = {
            "type": querytype,
            "words": words,
            "query": query,
            "concepts": concepts,
        }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "search.html", context)


def analyze(request):
    if request.method != "POST" or not request.POST.get("analyze_phrase_input"):
        return HttpResponseRedirect(reverse("home"))

    from datacore.functions.stanza import get_stanza, stanza_phrase_analysis

    from .models import Corpora, Document, PhraseCollection

    text = request.POST.get("analyze_phrase_input")
    if request.POST.get("analyze_phrase"):
        # setup pipeline
        nlp = get_stanza(
            lang="en", processors="tokenize,pos,lemma,depparse,ner,constituency"
        )
        doc = nlp(text)

        # Get or create corpora and phrase collection entries for user submissions
        corpora, created = Corpora.objects.get_or_create(title="Frontend Submissions")
        if len(doc.sentences) == 1:
            collection, created = PhraseCollection.objects.get_or_create(
                title="Submission Analysis Collections"
            )
            corpora.phrase_collections.add(collection)
            phrase, created = Phrase.objects.get_or_create(text=text)
            collection.phrases.add(phrase)
            result, analysis = stanza_phrase_analysis(
                phrase_item=phrase, sentence=doc.sentences[0]
            )
            context = {
                "phrase": phrase,
                "analysis": analysis,
            }
            return render(request, "analyze.html", context)
        else:
            document, created = Document.objects.get_or_create(content=text)
            phrases = []
            for sentence in doc.sentences:
                phrase, created = Phrase.objects.get_or_create(
                    text=sentence.text, document=document
                )
                if created and phrase not in document.phrases.all():
                    document.phrases.add(phrase)
                phrases.append(phrase)
                result, analysis = stanza_phrase_analysis(
                    phrase_item=phrase, sentence=sentence
                )
            context = {
                "document": document,
                "phrases": phrases,
            }
            return render(request, "analyze.html", context)


def corpora(request):
    from datacore.models import Corpora

    corpora = Corpora.objects.all().order_by("title")
    corpora, paginator_range = prepare_pagination(
        query=corpora, page=request.GET.get("page", 1)
    )
    context = {
        "corpora": corpora,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "corpora.html", context)


def corpora_add(request):
    return add_object(
        cls_form="CorpusForm",
        title=_("Add Corpus"),
        url_success_redirect="datacore:corpus",
        url="datacore:corpora_add",
        back_url="datacore:corpora",
        request=request,
    )


def corpus(request, id=None):
    from datacore.models import Corpora

    corpus = Corpora.objects.get(id=id)

    context = {
        "corpus": corpus,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "corpus.html", context)


def corpus_edit(request, id=None):
    return edit_object(
        cls_form="CorpusForm",
        cls_item="Corpora",
        title=_("Edit Corpus"),
        url_success_redirect="datacore:corpus",
        url="datacore:corpus_edit",
        request=request,
        id=id,
    )


def corpus_delete(request, id=None):
    return delete_object(
        cls_item="Corpora",
        title=_("Delete Corpus"),
        url_success_redirect="datacore:corpora",
        url="datacore:corpus_delete",
        back_url="datacore:corpus",
        request=request,
        id=id,
    )


def corpus_documents(request, id=None):
    from datacore.models import Corpora, Document

    corpus = Corpora.objects.get(id=id)

    if request.method == "POST" and request.POST.get("id"):
        document_id = request.POST.get("id")
        if request.POST.get("remove") == "1" or (
            request.htmx and request.htmx.trigger_name == "remove"
        ):
            corpus.documents.remove(document_id)
        if request.POST.get("delete") == "1" or (
            request.htmx and request.htmx.trigger_name == "delete"
        ):
            Document.objects.filter(id=document_id).delete()

    documents = corpus.documents.all()
    documents, paginator_range = prepare_pagination(
        query=documents, page=request.GET.get("page", 1), items_per_page=24
    )
    context = {
        "corpus": corpus,
        "documents": documents,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "corpus-documents.html", context)


def corpus_documents_add(request, id=None):
    return add_relationship_by_search(
        cls_item="Corpora",
        cls_relation="Document",
        relation="documents",
        title=_("Search Documents"),
        url=reverse("datacore:corpus_documents_add", args=[id]),
        back_url=reverse("datacore:corpus_documents", args=[id]),
        request=request,
        id=id,
    )


def corpus_phrase_collections(request, id=None):
    from datacore.models import Corpora, PhraseCollection

    corpus = Corpora.objects.get(id=id)

    if request.method == "POST" and request.POST.get("id"):
        collection_id = request.POST.get("id")
        if request.POST.get("remove") == "1" or (
            request.htmx and request.htmx.trigger_name == "remove"
        ):
            corpus.phrase_collections.remove(collection_id)
        if request.POST.get("delete") == "1" or (
            request.htmx and request.htmx.trigger_name == "delete"
        ):
            PhraseCollection.objects.filter(id=collection_id).delete()

    collections = corpus.phrase_collections.all()
    collections, paginator_range = prepare_pagination(
        query=collections, page=request.GET.get("page", 1), items_per_page=24
    )
    context = {
        "corpus": corpus,
        "collections": collections,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "corpus-phrase-collections.html", context)


def corpus_phrase_collections_add(request, id=None):
    return add_relationship_by_search(
        cls_item="Corpora",
        cls_relation="PhraseCollection",
        relation="phrase_collections",
        title=_("Search Phrase Collections"),
        url=reverse("datacore:corpus_phrase_collections_add", args=[id]),
        back_url=reverse("datacore:corpus_phrase_collections", args=[id]),
        request=request,
        id=id,
    )


def phrase_collections(request):
    from datacore.models import PhraseCollection

    phrase_collections = PhraseCollection.objects.all()
    phrase_collections, paginator_range = prepare_pagination(
        query=phrase_collections, page=request.GET.get("page", 1), items_per_page=24
    )
    context = {
        "phrase_collections": phrase_collections,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "phrase-collections.html", context)


def phrase_collections_add(request):
    return add_object(
        cls_form="PhraseCollectionForm",
        title=_("Add Phrase Collection"),
        url_success_redirect="datacore:phrase_collection",
        url="datacore:phrase_collections_add",
        back_url="datacore:phrase_collections",
        request=request,
    )


def phrase_collection(request, id=None):
    from datacore.models import Phrase, PhraseCollection

    phrase_collection = get_object_or_404(PhraseCollection, id=id)

    if request.method == "POST":
        phrase = get_object_or_404(Phrase, id=request.POST.get("phrase-id"))
        if request.POST.get("remove-phrase") is not None or (
            request.htmx and request.htmx.trigger_name == "remove-phrase"
        ):
            phrase_collection.phrases.remove(phrase)
        if request.POST.get("delete-phrase") is not None or (
            request.htmx and request.htmx.trigger_name == "delete-phrase"
        ):
            phrase.delete()

    context = {
        "id": id,
        "phrase_collection": phrase_collection,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "phrase-collection.html", context)


def phrase_collection_add_phrase(request, id=None):
    from datacore.forms import PhraseForm
    from datacore.models import PhraseCollection

    item = get_object_or_404(PhraseCollection, id=id)
    form = PhraseForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            phrase = form.save()
            item.phrases.add(phrase)
            return HttpResponseRedirect(
                reverse("datacore:phrase_collection", args=[id])
            )
        else:
            phrase, created = Phrase.objects.get_or_create(
                text=form.cleaned_data["text"], language=form.cleaned_data["language"]
            )
            phrase.data_sources.set(form.cleaned_data["data_sources"])
            item.phrases.add(phrase)
            return HttpResponseRedirect(
                reverse("datacore:phrase_collection", args=[id])
            )

    context = {
        "title": _("Add Phrase"),
        "url": reverse("datacore:phrase_collection_add_phrase", args=[id]),
        "back_url": reverse("datacore:phrase_collection", args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def phrase_collection_edit(request, id=None):
    return edit_object(
        cls_form="PhraseCollectionForm",
        cls_item="PhraseCollection",
        title=_("Edit Phrase Collection"),
        url_success_redirect="datacore:phrase_collection",
        url="datacore:phrase_collection_edit",
        request=request,
        id=id,
    )


def phrase_collection_delete(request, id=None):
    return delete_object(
        cls_item="PhraseCollection",
        title=_("Delete Phrase Collection"),
        url_success_redirect="datacore:phrase_collections",
        url="datacore:phrase_collection_delete",
        back_url="datacore:phrase_collection",
        request=request,
        id=id,
    )


def words(request):
    from datacore.forms import WordsFilter
    from datacore.models import Word

    queryset, parameters = None, ""
    form = WordsFilter()
    if request.method == "GET":
        form = WordsFilter(request.GET)
        if request.GET.get("filter-submit") and form.is_valid():
            sort_type = (
                form.cleaned_data["sort_type"]
                if form.cleaned_data["sort_type"]
                in [item[0] for item in WordsFilter.SORT_TYPE]
                else WordsFilter.SORT_TYPE[0][0]
            )
            sort_by = (
                form.cleaned_data["sort_by"]
                if form.cleaned_data["sort_by"]
                in [item[0] for item in WordsFilter.SORT_BY]
                else WordsFilter.SORT_BY[0][0]
            )
            queryset = Word.filter_words(
                start=form.cleaned_data["start"],
                contain=form.cleaned_data["contain"],
                end=form.cleaned_data["end"],
                sort_by=sort_by,
                sort_type=sort_type,
            )
    words = Word.objects.all().order_by("text") if queryset is None else queryset
    if queryset:
        words, paginator_range, parameters = prepare_pagination(
            query=words,
            page=request.GET.get("page", 1),
            items_per_page=30,
            request_parameters=request.GET,
        )
    else:
        words, paginator_range = prepare_pagination(
            query=words, page=request.GET.get("page", 1), items_per_page=30
        )
    context = {
        "words": words,
        "filter_form": form,
        "paginator_range": paginator_range,
        "parameters": parameters,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "words.html", context)


def words_add(request):
    return add_object(
        cls_form="WordForm",
        title=_("Add Word"),
        url_success_redirect="datacore:word",
        url="datacore:words_add",
        back_url="datacore:words",
        request=request,
    )


def word(request, id=None):
    from datacore.models import Word, WordRelation

    word = Word.objects.get(id=id)
    concepts = Concept.objects.filter(synonyms=word).all()
    relations = WordRelation.objects.filter(words__contains=[id]).all()
    words_ids = []
    for rel in relations:
        if rel.words[0] not in words_ids:
            words_ids.append(rel.words[0])
        if rel.words[1] not in words_ids:
            words_ids.append(rel.words[1])
    related_words = dict(
        {(item.id, item) for item in Word.objects.filter(id__in=words_ids).all()}
    )
    context = {
        "word": word,
        "concepts": concepts,
        "relations": relations,
        "related_words": related_words,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word.html", context)


def word_edit(request, id=None):
    return edit_object(
        cls_form="WordForm",
        cls_item="Word",
        title=_("Edit Word"),
        url_success_redirect="datacore:word",
        url="datacore:word_edit",
        request=request,
        id=id,
    )


def word_delete(request, id=None):
    return delete_object(
        cls_item="Word",
        title=_("Delete Word"),
        url_success_redirect="datacore:words",
        url="datacore:word_delete",
        back_url="datacore:word",
        request=request,
        id=id,
    )


def entities(request):
    from datacore.models import NamedEntity

    entities = NamedEntity.objects.all().order_by("text")
    entities, paginator_range = prepare_pagination(
        query=entities, page=request.GET.get("page", 1), items_per_page=24
    )
    context = {
        "entities": entities,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "entities.html", context)


def entities_add(request):
    return add_object(
        cls_form="NamedEntityForm",
        title=_("Add Named Entities"),
        url_success_redirect="datacore:entity",
        url="datacore:entities_add",
        back_url="datacore:entities",
        request=request,
    )


def entity(request, id=None):
    from datacore.models import NamedEntity

    entity = NamedEntity.objects.get(id=id)
    context = {
        "entity": entity,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "entity.html", context)


def entity_edit(request, id=None):
    return edit_object(
        cls_form="NamedEntityForm",
        cls_item="NamedEntity",
        title=_("Edit Named Entity"),
        url_success_redirect="datacore:entity",
        url="datacore:entity_edit",
        request=request,
        id=id,
    )


def entity_delete(request, id=None):
    return delete_object(
        cls_item="NamedEntity",
        title=_("Delete Named Entity"),
        url_success_redirect="datacore:entities",
        url="datacore:entity_delete",
        back_url="datacore:entity",
        request=request,
        id=id,
    )


def domain_ontologies(request):
    from datacore.models import DomainOntology

    domains = DomainOntology.objects.all().order_by("title")
    domains, paginator_range = prepare_pagination(
        query=domains, page=request.GET.get("page", 1)
    )
    context = {
        "domains": domains,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "domain-ontologies.html", context)


def domain_ontologies_add(request):
    return add_object(
        cls_form="DomainOntologyForm",
        title=_("Add Domain Ontology"),
        url_success_redirect="datacore:domain_ontology",
        url="datacore:domain_ontologies_add",
        back_url="datacore:domain_ontologies",
        request=request,
    )


def domain_ontology(request, id=None):
    from datacore.models import DomainOntology

    domain = DomainOntology.objects.get(id=id)

    concepts = Concept.objects.filter(ontology_domain=id)
    concepts, paginator_range = prepare_pagination(
        query=concepts, page=request.GET.get("page", 1)
    )
    context = {
        "id": id,
        "domain": domain,
        "concepts": concepts,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "domain-ontology.html", context)


def domain_ontology_concept_add(request, id=None):
    from datacore.forms import ConceptForm
    from datacore.models import DomainOntology

    item = get_object_or_404(DomainOntology, id=id)
    form = ConceptForm(request.POST or None, initial={"ontology_domain": id})
    field = form.fields["ontology_domain"]
    field.widget = field.hidden_widget()

    if request.method == "POST":
        if form.is_valid():
            concept = form.save()
            return HttpResponseRedirect(reverse("datacore:concept", args=[concept.id]))
        # else:
        #     concept, created = Concept.objects.get_or_create(pos=form.cleaned_data["text"], language=form.cleaned_data["language"])
        #     phrase.data_sources.set(form.cleaned_data['data_sources'])
        #     return HttpResponseRedirect(reverse('datacore:concept', args=[concept.id]))

    context = {
        "title": _("Add Concept to Domain Ontology"),
        "item": item,
        "url": reverse("datacore:domain_ontology_concept_add", args=[id]),
        "back_url": reverse("datacore:domain_ontology", args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def domain_ontology_edit(request, id=None):
    return edit_object(
        cls_form="DomainOntologyForm",
        cls_item="DomainOntology",
        title=_("Edit Domain Ontology"),
        url_success_redirect="datacore:domain_ontology",
        url="datacore:domain_ontology_edit",
        request=request,
        id=id,
    )


def domain_ontology_delete(request, id=None):
    return delete_object(
        cls_item="DomainOntology",
        title=_("Delete Domain Ontology"),
        url_success_redirect="datacore:domain_ontologies",
        url="datacore:domain_ontology_delete",
        back_url="datacore:domain_ontology",
        request=request,
        id=id,
    )


def documents(request):
    from datacore.models import Document

    documents = Document.objects.all()
    documents, paginator_range = prepare_pagination(
        query=documents, page=request.GET.get("page", 1), items_per_page=24
    )
    context = {
        "documents": documents,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "documents.html", context)


def documents_add(request):
    return add_object(
        cls_form="DocumentForm",
        title=_("Add Documents"),
        url_success_redirect="datacore:document",
        url="datacore:documents_add",
        back_url="datacore:documents",
        request=request,
    )


def document(request, id=None):
    from datacore.models import Document

    document = Document.objects.get(id=id)

    if request.method == "POST":
        if request.POST.get("doc_tokenize_stanza"):
            from datacore.functions.stanza import stanza_tokenize_document

            stanza_tokenize_document(document)
        if request.POST.get("doc_tokenize_spacy"):
            from datacore.functions.spacy import spacy_document_tokenize

            spacy_document_tokenize(document)

    context = {
        "id": id,
        "document": document,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "document.html", context)


def document_edit(request, id=None):
    return edit_object(
        cls_form="DocumentForm",
        cls_item="Document",
        title=_("Edit Document"),
        url_success_redirect="datacore:document",
        url="datacore:document_edit",
        request=request,
        id=id,
    )


def document_delete(request, id=None):
    return delete_object(
        cls_item="Document",
        title=_("Delete Document"),
        url_success_redirect="datacore:documents",
        url="datacore:document_delete",
        back_url="datacore:document",
        request=request,
        id=id,
    )


def phrases(request):
    from datacore.models import Phrase

    phrases = Phrase.objects.all().order_by("text")
    phrases, paginator_range = prepare_pagination(
        query=phrases, page=request.GET.get("page", 1)
    )
    context = {
        "phrases": phrases,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "phrases.html", context)


def phrases_add(request):
    return add_object(
        cls_form="PhraseForm",
        title=_("Add Phrase"),
        url_success_redirect="datacore:phrase",
        url="datacore:phrases_add",
        back_url="datacore:phrases",
        request=request,
    )


def phrase(request, id=None):
    from datacore.models import Phrase, PhraseAnalysis

    phrase_object = Phrase.objects.get(id=id)

    if request.method == "POST":
        # Analyze
        if request.POST.get("phrase_analysis_stanza"):
            from datacore.functions.stanza import stanza_phrase_analysis

            stanza_phrase_analysis(phrase_item=phrase_object)
        if request.POST.get("phrase_analysis_spacy"):
            from datacore.functions.spacy import spacy_phrase_analysis

            spacy_phrase_analysis(phrase_item=phrase_object)

    # list documents with this phrase
    documents = Document.objects.filter(phrases__id=phrase_object.id)
    # List all analysis results of phrase
    analysis_results = PhraseAnalysis.objects.filter(phrase=phrase_object)
    context = {
        "id": id,
        "phrase": phrase_object,
        "documents": documents,
        "analysis_results": analysis_results,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "phrase.html", context)


def phrase_edit(request, id=None):
    return edit_object(
        cls_form="PhraseForm",
        cls_item="Phrase",
        title=_("Edit Phrase"),
        url_success_redirect="datacore:phrase",
        url="datacore:phrase_edit",
        request=request,
        id=id,
    )


def phrase_delete(request, id=None):
    return delete_object(
        cls_item="Phrase",
        title=_("Delete Phrase"),
        url_success_redirect="datacore:phrases",
        url="datacore:phrase_delete",
        back_url="datacore:phrase",
        request=request,
        id=id,
    )


def concepts(request):
    from datacore.models import Concept

    concepts = Concept.objects.all()
    concepts, paginator_range = prepare_pagination(
        query=concepts, page=request.GET.get("page", 1)
    )
    context = {
        "concepts": concepts,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concepts.html", context)


def concepts_add(request):
    return add_object(
        cls_form="ConceptForm",
        title=_("Add Concept"),
        url_success_redirect="datacore:concept",
        url="datacore:concepts_add",
        back_url="datacore:concepts",
        request=request,
    )


def get_concept_tab_data(id=None):
    return (
        (reverse("datacore:concept_synonyms", args=[id]), _("Synonyms")),
        (reverse("datacore:concept_antonyms", args=[id]), _("Antonyms")),
        (reverse("datacore:concept_definitions", args=[id]), _("Definitions")),
        (reverse("datacore:concept_examples", args=[id]), _("Examples")),
        (reverse("datacore:concept_relationships", args=[id]), _("Relationships")),
        (reverse("datacore:concept_visualization", args=[id]), _("Visualization")),
    )


def concept(request, id=None):
    from datacore.models import Concept

    concept = Concept.objects.get(id=id)

    context = {
        "id": id,
        "concept": concept,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_synonyms", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept.html", context)


def concept_synonyms(request, id=None):
    from datacore.models import Concept

    concept = Concept.objects.get(id=id)

    if request.POST:
        if request.POST.get("remove-item") is not None or (
            request.htmx and request.htmx.trigger_name == "remove-synonym-word"
        ):
            word = get_object_or_404(Word, id=request.POST.get("remove-item"))
            concept.synonyms.remove(word)

    context = {
        "id": id,
        "concept": concept,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_synonyms", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-synonyms.html", context)


def concept_synonyms_add(request, id=None):
    return add_relationship(
        cls_item="Concept",
        cls_relation="Word",
        relation="synonyms",
        cls_form="WordForm",
        title=_("Add Synonym"),
        url="datacore:concept_synonyms_add",
        back_url="datacore:concept_synonyms",
        request=request,
        id=id,
    )


def concept_synonym_edit(request, id=None, rel_id=None):
    return edit_relationship(
        cls_item="Concept",
        cls_relation="Word",
        relation="synonyms",
        cls_form="WordForm",
        title=_("Edit Synonym"),
        url="datacore:concept_synonym_edit",
        back_url="datacore:concept",
        request=request,
        id=id,
        rel_id=rel_id,
    )


def concept_antonyms(request, id=None):
    from datacore.models import Concept

    concept = Concept.objects.get(id=id)

    if request.POST:
        if request.POST.get("remove-item") is not None or (
            request.htmx and request.htmx.trigger_name == "remove-antonym-word"
        ):
            word = get_object_or_404(Word, id=request.POST.get("remove-item"))
            concept.antonyms.remove(word)

    context = {
        "id": id,
        "concept": concept,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_antonyms", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-antonyms.html", context)


def concept_antonyms_add(request, id=None):
    return add_relationship(
        cls_item="Concept",
        cls_relation="Word",
        relation="antonyms",
        cls_form="WordForm",
        title=_("Add Synonym"),
        url="datacore:concept_antonyms_add",
        back_url="datacore:concept_antonyms",
        request=request,
        id=id,
    )


def concept_antonym_edit(request, id=None, rel_id=None):
    return edit_relationship(
        cls_item="Concept",
        cls_relation="Word",
        relation="antonyms",
        cls_form="WordForm",
        title=_("Edit Antonym"),
        url="datacore:concept_antonym_edit",
        back_url="datacore:concept",
        request=request,
        id=id,
        rel_id=rel_id,
    )


def concept_definitions(request, id=None):
    from datacore.models import Concept, Definition

    concept = Concept.objects.get(id=id)

    if request.POST:
        if request.POST.get("remove-item") is not None or (
            request.htmx and request.htmx.trigger_name == "remove-definition"
        ):
            definition = get_object_or_404(
                Definition, id=request.POST.get("remove-item")
            )
            concept.definitions.remove(definition)

    context = {
        "id": id,
        "concept": concept,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_definitions", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-definitions.html", context)


def concept_definitions_add(request, id=None):
    return add_relationship(
        cls_item="Concept",
        cls_relation="Definition",
        relation="definitions",
        cls_form="DefinitionForm",
        title=_("Add Definition"),
        url="datacore:concept_definitions_add",
        back_url="datacore:concept_definitions",
        request=request,
        id=id,
    )


def concept_definition_edit(request, id=None, rel_id=None):
    return edit_relationship(
        cls_item="Concept",
        cls_relation="Definition",
        relation="definitions",
        cls_form="DefinitionForm",
        title=_("Edit Definition"),
        url="datacore:concept_definition_edit",
        back_url="datacore:concept",
        request=request,
        id=id,
        rel_id=rel_id,
    )


def concept_examples(request, id=None):
    from datacore.models import Concept

    concept = Concept.objects.get(id=id)

    if request.POST:
        if request.POST.get("remove-item") is not None or (
            request.htmx and request.htmx.trigger_name == "remove-example"
        ):
            example = get_object_or_404(Example, id=request.POST.get("remove-item"))
            concept.examples.remove(example)

    context = {
        "id": id,
        "concept": concept,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_examples", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-examples.html", context)


def concept_examples_add(request, id=None):
    return add_relationship(
        cls_item="Concept",
        cls_relation="Example",
        relation="examples",
        cls_form="ExampleForm",
        title=_("Add Example"),
        url="datacore:concept_examples_add",
        back_url="datacore:concept_examples",
        request=request,
        id=id,
    )


def concept_example_edit(request, id=None, rel_id=None):
    return edit_relationship(
        cls_item="Concept",
        cls_relation="Example",
        relation="examples",
        cls_form="ExampleForm",
        title=_("Edit Example"),
        url="datacore:concept_example_edit",
        back_url="datacore:concept",
        request=request,
        id=id,
        rel_id=rel_id,
    )


def concept_relationships(request, id=None):
    from datacore.models import Component, Concept, Relation

    concept = Concept.objects.get(id=id)

    # Remove relation
    if request.method == "POST" and (
        request.POST.get("remove-relation") == "1"
        or (request.htmx and request.htmx.trigger_name == "remove-relation")
    ):
        Relation.objects.get(id=request.POST.get("relation-id")).delete()

    # Create list of relationships as a cache to prevent multiple small queries
    relations = Relation.objects.filter(concepts__contains=[id]).all()
    concept_ids = []
    concept_rels = []
    for rel in relations:
        if rel.concepts[0] not in concept_ids:
            concept_ids.append(rel.concepts[0])
        if rel.concepts[1] not in concept_ids:
            concept_ids.append(rel.concepts[1])
        if rel.relation_type not in concept_rels:
            concept_rels.append(rel.relation_type)
    related_concepts = dict(
        {(item.id, item) for item in Concept.objects.filter(id__in=concept_ids).all()}
    )
    related_concept_rels = dict(
        {
            (item.code, item)
            for item in Component.objects.filter(code__in=concept_rels).all()
        }
    )

    if len(concept_rels) != len(related_concept_rels):
        raise Exception(
            f"""
            All queried relations where not found.
            Queried relations:  {concept_rels}
            Relations Found: {related_concept_rels}
            You might need to add missing relationships to `Linguistic Components > Ontology > Relation`
            \n"""
        )

    context = {
        "id": id,
        "concept": concept,
        "relations": relations,
        "related_concepts": related_concepts,
        "related_concept_rels": related_concept_rels,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_relationships", args=[id]),
    }

    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-relationships.html", context)


def concept_relationships_add(request, id=None):
    from datacore.forms import RelationForm

    form = RelationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(
                reverse("datacore:concept_relationships", args=[id])
            )

    context = {
        "title": _("Add Relation"),
        "url": reverse("datacore:concept_relationships_add", args=[id]),
        "back_url": reverse("datacore:concept_relationships", args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def concept_visualization(request, id=None):
    from datacore.models import Concept
    from django.core.files.storage import default_storage

    concept = Concept.objects.get(id=id)

    if request.method == "POST":
        from datacore.functions.visualization import (
            generate_hierarchy_graph,
            generate_neighborhood_graph,
            generate_relation_graph,
        )

        if request.POST.get("regenerate-relation") == "1" or (
            request.htmx and request.htmx.trigger_name == "regenerate-relation"
        ):
            generate_relation_graph(id)
        if request.POST.get("regenerate-hierarchy") == "1" or (
            request.htmx and request.htmx.trigger_name == "regenerate-hierarchy"
        ):
            generate_hierarchy_graph(id)
        if request.POST.get("regenerate-neighborhood") == "1" or (
            request.htmx and request.htmx.trigger_name == "regenerate-neighborhood"
        ):
            generate_neighborhood_graph(id, n=2)

    relation_path = (
        f"concept/{id}/relation.png"
        if default_storage.exists(f"concept/{id}/relation.png")
        else None
    )
    hierarchy_path = (
        f"concept/{id}/hierarchy.png"
        if default_storage.exists(f"concept/{id}/hierarchy.png")
        else None
    )
    neighborhood_path = (
        f"concept/{id}/neighborhood.png"
        if default_storage.exists(f"concept/{id}/neighborhood.png")
        else None
    )

    context = {
        "concept": concept,
        "relation_path": relation_path,
        "hierarchy_path": hierarchy_path,
        "neighborhood_path": neighborhood_path,
        "tab_data": get_concept_tab_data(id),
        "tab_active": reverse("datacore:concept_visualization", args=[id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "concept-visualization.html", context)


def templates(request):
    from django.db.models import Count

    templates = (
        Template.objects.all()
        .annotate(phrase_count=Count("phrase_template"))
        .order_by("-phrase_count")
    )  # .order_by('count')
    templates, paginator_range = prepare_pagination(
        query=templates, page=request.GET.get("page", 1)
    )
    context = {
        "templates": templates,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "templates.html", context)


def template(request, id=None):
    from datacore.models import Phrase, PhraseAnalysis, Template

    template_object = Template.objects.get(id=id)
    template_children = Template.objects.filter(parent=id)
    try:
        analysis_ids = [
            analysis["phrase"]
            for analysis in PhraseAnalysis.objects.filter(template=template_object)
            .values("phrase")
            .all()
        ]
        phrases = Phrase.objects.filter(id__in=analysis_ids)
    except Exception:
        phrases = []
    context = {
        "id": id,
        "template": template_object,
        "template_children": template_children,
        "phrases": phrases,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "template.html", context)


def components(request):
    from datacore.models import Component

    components = Component.objects.all()
    context = {
        "components": components,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "components.html", context)


def component(request, slug=None):
    from datacore.models import Component

    component = Component.objects.get(slug=slug)
    context = {
        "component": component,
    }
    return render(request, "component.html", context)


def languages(request):
    from datacore.models import Language

    languages = Language.objects.all()
    languages, paginator_range = prepare_pagination(
        query=languages, page=request.GET.get("page", 1), items_per_page=30
    )
    context = {
        "languages": languages,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "languages.html", context)


def languages_add(request):
    return add_object(
        cls_form="LanguageForm",
        title=_("Add Language"),
        url_success_redirect="language:word",
        url="datacore:languages_add",
        back_url="datacore:languages",
        request=request,
    )


def language(request, id=None):
    from datacore.models import Language

    language = Language.objects.get(id=id)
    context = {
        "language": language,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "language.html", context)


def language_edit(request, id=None):
    return edit_object(
        cls_form="LanguageForm",
        cls_item="Language",
        title=_("Edit Language"),
        url_success_redirect="datacore:language",
        url="datacore:language_edit",
        request=request,
        id=id,
    )


def language_delete(request, id=None):
    return delete_object(
        cls_item="Language",
        title=_("Delete Language"),
        url_success_redirect="datacore:languages",
        url="datacore:language_delete",
        back_url="datacore:language",
        request=request,
        id=id,
    )


def word_relation_types(request):
    from datacore.models import WordRelationType

    relation_types = WordRelationType.objects.all()
    relation_types, paginator_range = prepare_pagination(
        query=relation_types, page=request.GET.get("page", 1), items_per_page=30
    )
    context = {
        "relation_types": relation_types,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-relation-types.html", context)


def word_relation_types_add(request):
    return add_object(
        cls_form="WordRelationTypeForm",
        title=_("Add Word-Relation Type"),
        url_success_redirect="datacore:word_relation_type",
        url="datacore:word_relation_types_add",
        back_url="datacore:word_relation_types",
        request=request,
    )


def word_relation_type(request, id=None):
    from datacore.models import WordRelation, WordRelationType

    relation_type = WordRelationType.objects.get(id=id)
    relations = WordRelation.objects.filter(word_relation=relation_type).all()
    words_ids = []
    for rel in relations:
        if rel.words[0] not in words_ids:
            words_ids.append(rel.words[0])
        if rel.words[1] not in words_ids:
            words_ids.append(rel.words[1])
    related_words = dict(
        {(item.id, item) for item in Word.objects.filter(id__in=words_ids).all()}
    )
    relations, paginator_range = prepare_pagination(
        query=relations, page=request.GET.get("page", 1)
    )
    context = {
        "relation_type": relation_type,
        "relations": relations,
        "related_words": related_words,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-relation-type.html", context)


def word_relation_type_edit(request, id=None):
    return edit_object(
        cls_form="WordRelationTypeForm",
        cls_item="WordRelationType",
        title=_("Edit Word Relation Type"),
        url_success_redirect="datacore:word_relation_type",
        url="datacore:word_relation_type_edit",
        request=request,
        id=id,
    )


def word_relation_type_delete(request, id=None):
    return delete_object(
        cls_item="WordRelationType",
        title=_("Delete Word Relation Type"),
        url_success_redirect="datacore:word_relation_types",
        url="datacore:word_relation_type_delete",
        back_url="datacore:word_relation_type",
        request=request,
        id=id,
    )


def word_relations(request, id=None):
    from datacore.models import WordRelation

    relations = WordRelation.objects.all()
    relations, paginator_range = prepare_pagination(
        query=relations, page=request.GET.get("page", 1), items_per_page=30
    )
    # Get words related to relations
    words_ids = []
    for rel in relations:
        if rel.words[0] not in words_ids:
            words_ids.append(rel.words[0])
        if rel.words[1] not in words_ids:
            words_ids.append(rel.words[1])
    related_words = dict(
        {(item.id, item) for item in Word.objects.filter(id__in=words_ids).all()}
    )
    context = {
        "relations": relations,
        "related_words": related_words,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-relations.html", context)


def word_relation(request, id=None):
    from datacore.models import WordRelation

    relation = WordRelation.objects.get(id=id)
    words_ids = [relation.words[0], relation.words[1]]
    related_words = dict(
        {(item.id, item) for item in Word.objects.filter(id__in=words_ids).all()}
    )
    context = {
        "relation": relation,
        "related_words": related_words,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-relation.html", context)


def word_relations_add(request):
    from datacore.forms import WordRelationForm
    from datacore.models import Word, WordRelation

    form = WordRelationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            word_one, created = Word.objects.get_or_create(
                text=form.cleaned_data["word_one"],
                language=form.cleaned_data["word_one_language"],
            )
            word_two, created = Word.objects.get_or_create(
                text=form.cleaned_data["word_two"],
                language=form.cleaned_data["word_two_language"],
            )
            item, saved = WordRelation.objects.get_or_create(
                words=[word_one.id, word_two.id],
                word_relation=form.cleaned_data["word_relation"],
            )
            item.data_sources.set(form.cleaned_data["data_sources"])
            return HttpResponseRedirect(
                reverse("datacore:word_relation", args=[item.id])
            )

    context = {
        "title": _("Edit Word Relationship"),
        "url": reverse("datacore:word_relations_add"),
        "back_url": reverse("datacore:word_relations"),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def word_relation_edit(request, id=None):
    return edit_object(
        cls_form="WordRelationEditForm",
        cls_item="WordRelation",
        title=_("Edit Word Relation"),
        url_success_redirect="datacore:word_relation",
        url="datacore:word_relation_edit",
        request=request,
        id=id,
    )


def word_relation_delete(request, id=None):
    return delete_object(
        cls_item="WordRelation",
        title=_("Delete Word Relation"),
        url_success_redirect="datacore:word_relations",
        url="datacore:word_relation_delete",
        back_url="datacore:word_relation",
        request=request,
        id=id,
    )


def word_lists(request, id=None):
    from datacore.models import WordList

    word_lists = WordList.objects.all()
    word_lists, paginator_range = prepare_pagination(
        query=word_lists, page=request.GET.get("page", 1), items_per_page=30
    )
    context = {
        "word_lists": word_lists,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-lists.html", context)


def word_lists_add(request):
    return add_object(
        cls_form="WordListForm",
        title=_("Add Word List"),
        url_success_redirect="datacore:word_list",
        url="datacore:word_lists_add",
        back_url="datacore:word_lists",
        request=request,
    )


def word_list(request, id=None):
    from datacore.models import WordList

    word_list = WordList.objects.get(id=id)
    context = {
        "word_list": word_list,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "word-list.html", context)


def word_list_edit(request, id=None):
    return edit_object(
        cls_form="WordListForm",
        cls_item="WordList",
        title=_("Edit Word List"),
        url_success_redirect="datacore:word_list",
        url="datacore:word_list_edit",
        request=request,
        id=id,
    )


def word_list_delete(request, id=None):
    return delete_object(
        cls_item="WordList",
        title=_("Delete Word List"),
        url_success_redirect="datacore:word_lists",
        url="datacore:word_list_delete",
        back_url="datacore:word_list",
        request=request,
        id=id,
    )


def word_list_word_add(request, id=None):
    from datacore.forms import WordForm
    from datacore.models import Word, WordList

    item = get_object_or_404(WordList, id=id)
    form = WordForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            word = form.save()
            item.words.add(word)
            return HttpResponseRedirect(reverse("datacore:word_list", args=[id]))
        else:
            word, created = Word.objects.get_or_create(
                text=form.cleaned_data["text"], language=form.cleaned_data["language"]
            )
            item.words.add(word)
            return HttpResponseRedirect(reverse("datacore:word_list", args=[id]))

    context = {
        "title": _("Add Word"),
        "url": reverse("datacore:word_list_word_add", args=[id]),
        "back_url": reverse("datacore:word_list", args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def data_sources(request, id=None):
    from datacore.models import DataSource

    data_sources = DataSource.objects.all()
    data_sources, paginator_range = prepare_pagination(
        query=data_sources, page=request.GET.get("page", 1)
    )
    context = {
        "data_sources": data_sources,
        "paginator_range": paginator_range,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "data-sources.html", context)


def data_sources_add(request):
    return add_object(
        cls_form="DataSourceForm",
        title=_("Add Data Source"),
        url_success_redirect="datacore:data_source",
        url="datacore:data_sources_add",
        back_url="datacore:data_sources",
        request=request,
    )


def data_source(request, id=None):
    from datacore.models import DataSource

    data_source = DataSource.objects.get(id=id)

    # Remove references
    if request.method == "POST" and request.POST.get("ref-id"):
        ref_id = request.POST.get("ref-id")
        if request.POST.get("remove_reference") == "1" or (
            request.htmx and request.htmx.trigger_name == "remove_reference"
        ):
            data_source.references.remove(ref_id)

    context = {
        "id": id,
        "data_source": data_source,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "data-source.html", context)


def data_source_edit(request, id=None):
    return edit_object(
        cls_form="DataSourceForm",
        cls_item="DataSource",
        title=_("Edit Data Source"),
        url_success_redirect="datacore:data_source",
        url="datacore:data_source_edit",
        request=request,
        id=id,
    )


def data_source_delete(request, id=None):
    return delete_object(
        cls_item="DataSource",
        title=_("Delete Data Source"),
        url_success_redirect="datacore:data_sources",
        url="datacore:data_source_delete",
        back_url="datacore:data_source",
        request=request,
        id=id,
    )


def data_source_add_references(request, id=None):
    from datacore.forms import ReferenceForm
    from datacore.models import DataSource, Reference

    item = get_object_or_404(DataSource, id=id)
    form = ReferenceForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            ref = form.save()
            item.references.add(ref)
            return HttpResponseRedirect(reverse("datacore:data_source", args=[id]))
        else:
            ref, created = Reference.objects.get_or_create(
                text=form.cleaned_data["text"], language=form.cleaned_data["language"]
            )
            item.references.add(ref)
            return HttpResponseRedirect(reverse("datacore:data_source", args=[id]))

    context = {
        "title": _("Add Reference"),
        "url": reverse("datacore:data_source_add_references", args=[id]),
        "back_url": reverse("datacore:data_source", args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def lexical_data(request):
    import os

    from django.core.files.storage import default_storage

    try:
        path = default_storage.path(os.path.join("export", "lexical"))
        files = os.listdir(path)
        files = {
            f: default_storage.url(os.path.join(path, f))
            for f in files
            if os.path.isfile(path + "/" + f) and f.endswith(".csv")
        }
    except Exception:
        files = {}

    context = {
        "files": files,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "export-lexical.html", context)


def lexical_data_export(request):
    # TODO: add fields: file name, language, named entities
    from datacore.forms import LexicalExportForm

    form = LexicalExportForm(request.POST or None)

    if request.POST.get("form-action") == "1" or (
        request.htmx and request.htmx.trigger_name == "form-action"
    ):
        if form.is_valid():
            from datacore.functions.export import export_lexical_data

            export_lexical_data(
                start=form.cleaned_data["start"],
                contain=form.cleaned_data["contain"],
                end=form.cleaned_data["end"],
                sort_by=form.cleaned_data["sort_by"],
                sort_type=form.cleaned_data["sort_type"],
                limit=form.cleaned_data["limit"],
            )
            return HttpResponseRedirect(reverse("datacore:lexical_data"))

    context = {
        "title": _("Export Lexical Data"),
        "action_title": _("Export"),
        "url": reverse("datacore:lexical_data_export"),
        "back_url": reverse("datacore:lexical_data"),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def textual_data(request):
    import os

    from django.core.files.storage import default_storage

    def get_textual_export_paths(path):
        try:
            path = default_storage.path(os.path.join("export", "textual", path))
            files_list = os.listdir(path)
            files = {
                f: default_storage.url(os.path.join(path, f))
                for f in files_list
                if os.path.isfile(path + "/" + f) and f.endswith(".zip")
            }
            return files
        except Exception:
            return {}

    files = {
        "all_corpora": get_textual_export_paths("all_corpora"),
        "all_documents": get_textual_export_paths("all_documents"),
        "all_phrases": get_textual_export_paths("all_phrases"),
    }

    context = {
        "files": files,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "export-textual.html", context)


def textual_data_export(request):
    from datacore.forms import TextualExportForm

    form = TextualExportForm(request.POST or None)

    if request.POST.get("form-action") == "1" or (
        request.htmx and request.htmx.trigger_name == "form-action"
    ):
        if form.is_valid():
            from datacore.functions.export import export_textual_data

            export_textual_data(import_type=form.cleaned_data["import_type"])
            return HttpResponseRedirect(reverse("datacore:textual_data"))

    context = {
        "title": _("Export Textual Data"),
        "action_title": _("Export"),
        "url": reverse("datacore:textual_data_export"),
        "back_url": reverse("datacore:textual_data"),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def ontological_data(request):
    import os

    from django.core.files.storage import default_storage

    try:
        path = default_storage.path(os.path.join("export", "ontological"))
        files = os.listdir(path)
        files = {
            f: default_storage.url(os.path.join(path, f))
            for f in files
            if os.path.isfile(path + "/" + f) and f.endswith(".csv")
        }
    except Exception:
        files = {}

    context = {
        "files": files,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "export-ontological.html", context)


def ontological_data_export(request):
    from datacore.forms import DomainOntologyExportForm

    form = DomainOntologyExportForm(request.POST or None)

    if request.POST.get("form-action") == "1" or (
        request.htmx and request.htmx.trigger_name == "form-action"
    ):
        if form.is_valid():
            from datacore.functions.export import export_ontological_data

            export_ontological_data(
                ontology_domain=form.cleaned_data["domain_ontology"],
                language=form.cleaned_data["language"],
            )
            return HttpResponseRedirect(reverse("datacore:ontological_data"))

    context = {
        "title": _("Export Domain Ontology Data"),
        "action_title": _("Export"),
        "url": reverse("datacore:ontological_data_export"),
        "back_url": reverse("datacore:ontological_data"),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def add_object(cls_form, title, url_success_redirect, url, back_url, request):
    """
    Handles loading form in modal or page, and saving object
    cls_form: the form name used to add object
    title: title of modal and page
    url_success_redirect: in case object is created, redirect to object's page
            note: only usefull if id is used, othewise leave empty to ignore
    url: url of item's page for adding object
    back_url: url for button to go back to item's page
    request: default view parameters
    """
    from datacore import forms

    FormClass = getattr(forms, cls_form)
    form = FormClass(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            item = form.save()
            if url_success_redirect:
                return HttpResponseRedirect(
                    reverse(url_success_redirect, args=[item.id])
                )
            else:
                return reverse(back_url)

    context = {
        "title": title,
        "url": reverse(url),
        "back_url": reverse(back_url),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def edit_object(cls_form, cls_item, url_success_redirect, title, url, request, id=None):
    """
    Handles loading form in modal or page for editing object
    cls_form: the form name used to edit object
    cls_item: the model name used to edit object
    title: title of modal and page
    url_success_redirect: in case object is edited, redirect to object's page
    url: url of item's edit page
    back_url: url for button to go back to item's page
    request: default view parameters
    id: id of item which is being edited
    """
    from datacore import forms
    from django.apps import apps

    ItemModel = apps.get_model("datacore", cls_item)
    FormClass = getattr(forms, cls_form)
    item = get_object_or_404(ItemModel, id=id)

    if request.method == "POST":
        form = FormClass(request.POST, instance=item)
        if form.is_valid():
            item = form.save()
            url_success_redirect = (
                request.POST.force_url_success_redirect
                if request.POST.force_url_success_redirect
                else url_success_redirect
            )
            return HttpResponseRedirect(reverse(url_success_redirect, args=[item.id]))

    form = FormClass(instance=item)
    context = {
        "title": title,
        "url": reverse(url, args=[item.id]),
        "item": item,
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def delete_object(
    cls_item, title, url_success_redirect, url, back_url, request, id=None
):
    """
    Handles loading modal for confiriming action and deleting object
    cls_item: the model name used to delete object
    title: title of modal and page
    url_success_redirect: in case object is deleted, redirect to parent's page
    url: url of item's delete page
    back_url: url for button to go back to item's page
    request: default view parameters
    id: id of item which is being deleted
    """
    from django.apps import apps

    ItemModel = apps.get_model("datacore", cls_item)
    item = get_object_or_404(ItemModel, id=id)

    if request.method == "DELETE":
        item.delete()
        return HttpResponseRedirect(reverse(url_success_redirect))

    context = {
        "title": title,
        "item": item,
        "url": reverse(url, args=[item.id]),
        "back_url": reverse(back_url, args=[item.id]),
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-delete.html", context)


def edit_relationship(
    cls_item,
    cls_relation,
    cls_form,
    relation,
    title,
    url,
    back_url,
    request,
    id=None,
    rel_id=None,
):
    """
    Handles editing manytomany relationship, using forms and by ignoring duplicates(get_or_create)
    cls_item: Model class of the item type
    cls_relation: model class of relation item type
    relation: method to access manytomany relationship
            E.g. for adding relationship the `corpus.documents` we'll have `cls_item='Corpora'`, `cls_relation='Document'`, and `relation="documents"`
    title: title of search model/page
    url: url of item's page for adding relationship
    back_url: url for button to go back to item's page
    request, id: default view parameters
    """
    from datacore import forms
    from django.apps import apps

    ItemModel = apps.get_model("datacore", cls_item)
    RelationModel = apps.get_model("datacore", cls_relation)
    FormClass = getattr(forms, cls_form)
    item = get_object_or_404(ItemModel, id=id)
    rel_item = get_object_or_404(RelationModel, id=rel_id)
    form = FormClass(request.POST or None, instance=rel_item)
    # used in relationships to fill fields which should be filtered using parent
    if hasattr(form, "parent_initialize") and callable(form.parent_initialize):
        form.parent_initialize(parent=item)

    if request.method == "POST":
        if form.is_valid():
            # check if item already is associated with other ItemModel relations; if so, create new item
            count = ItemModel.objects.filter(**{relation + "__id": rel_item.id}).count()
            form = (
                FormClass(request.POST or None) if count > 1 else form
            )  # create new item, otherwise edit
            form.save()
            return HttpResponseRedirect(reverse(back_url, args=[id]))

    context = {
        "title": title,
        "url": reverse(url, args=[id, rel_id]),
        "back_url": reverse(back_url, args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def add_relationship(
    cls_item, cls_relation, cls_form, relation, title, url, back_url, request, id=None
):
    """
    Handles adding manytomany relationship in modal, using forms and by ignoring duplicates
    cls_item: Model class of the item type
    cls_relation: model class of relation item type
    relation: method to access manytomany relationship
            E.g. for adding relationship the `corpus.documents` we'll have `cls_item='Corpora'`, `cls_relation='Document'`, and `relation="documents"`
    title: title of search model/page
    url: url of item's page for adding relationship
    back_url: url for button to go back to item's page
    request, id: default view parameters
    """
    from datacore import forms
    from django.apps import apps

    ItemModel = apps.get_model("datacore", cls_item)
    RelationModel = apps.get_model("datacore", cls_relation)
    FormClass = getattr(forms, cls_form)
    item = get_object_or_404(ItemModel, id=id)
    form = FormClass(request.POST or None)
    # `parent_initialize` is used in relationships to fill fields which should be filtered using parent
    if hasattr(form, "parent_initialize") and callable(form.parent_initialize):
        form.parent_initialize(parent=item)

    if request.method == "POST":
        if form.is_valid():
            # Create new item and add relationship
            relation_item = form.save()
            getattr(item, relation).add(relation_item)
        else:
            # in case of duplicates, get item and add relationship
            error_codes = (
                [item.code for item in form.errors["__all__"].as_data()]
                if "__all__" in form.errors
                else []
            )
            if error_codes == ["unique_together"]:
                relation_item, created = RelationModel.objects.get_or_create(
                    **form.cleaned_data
                )
                getattr(item, relation).add(relation_item)
        return HttpResponseRedirect(reverse(back_url, args=[id]))

    context = {
        "title": title,
        "url": reverse(url, args=[id]),
        "back_url": reverse(back_url, args=[id]),
        "form": form,
    }
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, "modal-body.html", context)


def add_relationship_by_search(
    cls_item,
    cls_relation,
    relation,
    title,
    url,
    back_url,
    request,
    id=None,
    search_field="title",
):
    """
    Handles search, adding, and removing manytomany relationship in modal
    cls_item: Model class of the item type
    cls_relation: model class of relation item type
    relation: method to access manytomany relationship
            E.g. for adding relationship the `corpus.documents` we'll have `cls_item='Corpora'`, `cls_relation='Document'`, and `relation="documents"`
    title: title of search model/page
    url: url of item's page for adding relationship
    back_url: url for button to go back to item's page
    request, id: default view parameters
    """
    from django.apps import apps

    ItemModel = apps.get_model("datacore", cls_item)
    RelationModel = apps.get_model("datacore", cls_relation)

    item = get_object_or_404(ItemModel, id=id)
    search_items, search_term = None, ""

    if (request.method == "POST" and request.POST.get("search")) or (
        request.htmx and request.htmx.trigger_name == "search"
    ):
        search_term = request.POST.get("search")
        # instead of `title__icontains=search_term`, we use `**{search_field+'__icontains':search_term}` parameter so that other fields for models which don't have title field can be searched
        search_items = (
            RelationModel.objects.filter(
                **{search_field + "__icontains": search_term}
            ).all()
            if search_term
            else None
        )

    if (request.method == "POST" and request.POST.get("add-relation-item")) or (
        request.htmx and request.htmx.trigger_name == "add-relation-item"
    ):
        relation_item = get_object_or_404(RelationModel, id=request.POST.get("item-id"))
        getattr(item, relation).add(relation_item)

    if (request.method == "POST" and request.POST.get("remove-relation-item")) or (
        request.htmx and request.htmx.trigger_name == "remove-relation-item"
    ):
        relation_item = get_object_or_404(RelationModel, id=request.POST.get("item-id"))
        getattr(item, relation).remove(relation_item)

    context = {
        "title": title,
        "item": item,
        "search_term": search_term,
        "search_items": search_items,
        "relation": relation,  # E.g. indicates `corpus.documents` if `item=Corpus` and `relation="document"` in template to dynamically set relationship
        "url": url,
        "back_url": back_url,
    }
    template = (
        "modal-item-search.html"
        if (
            request.htmx.trigger_name
            in ["search", "add-relation-item", "remove-relation-item"]
        )
        else "modal-search.html"
    )
    context["base_template"] = "partial.html" if request.htmx else "base.html"
    return render(request, template, context)

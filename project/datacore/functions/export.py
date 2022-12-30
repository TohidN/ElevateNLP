import os
import re
import unicodedata
from datetime import datetime

from django.core.files.storage import default_storage


def slugify(value, allow_unicode=False):
    """
    convert value into valid file/directory name
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


def get_dir(path):
    # get or create directory
    path = default_storage.path(path)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def zip_and_delete_dir(filename, root_dir, destination_path):
    """
    filename: name of zip file. without `.zip` extension
    root_dir: directory which will be compressed
    destination_path: zip file will be moved to this directory
    """
    import shutil

    shutil.make_archive(filename, "zip", root_dir)
    shutil.move(f"{filename}.zip", destination_path)
    shutil.rmtree(root_dir, ignore_errors=True)


def export_documents(path, documents):
    for document in documents:
        document_path = os.path.join(path, slugify(document.title) + ".txt")
        with open(document_path, "w", encoding="utf-8") as file:
            file.write(document.title + "\n")
            file.write(document.content)
        # create document phrase collection
        document_phrase_collection_path = get_dir(
            os.path.join(path, slugify(document.title) + "_phrase_collections")
        )
        for collection in document.phrase_collections.all():
            collection_path = os.path.join(
                document_phrase_collection_path, slugify(collection.title) + ".txt"
            )
            with open(collection_path, "w", encoding="utf-8") as file:
                file.write(collection.title + "\n")
                for phrase in collection.phrases.all():
                    file.write(phrase.text + "\n")


def export_phrase_collections(path, collections):
    for collection in collections:
        collection_path = os.path.join(path, slugify(collection.title) + ".txt")
        with open(collection_path, "w", encoding="utf-8") as file:
            file.write(collection.title + "\n")
            for phrase in collection.phrases.all():
                file.write(phrase.text + "\n")


def export_phrases(path, phrases):
    with open(path, "w", encoding="utf-8") as file:
        for phrase in phrases:
            file.write(phrase.text + "\n")


def export_lexical_data(
    start="", contain="", end="", sort_by="", sort_type="", limit=0
):
    from datacore.models import Word

    queryset = Word.filter_words(
        start=start,
        contain=contain,
        end=end,
        sort_by=sort_by,
        sort_type=sort_type,
        limit=limit,
    )
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_path = get_dir(os.path.join("export", "lexical"))
    path = os.path.join(base_path, current_time + ".csv")
    with open(path, "w", encoding="utf-8") as file:
        for item in queryset:
            file.write(item.text + "\n")
    return path


def export_textual_data(import_type):
    # TODO: Add meta-data files
    from datacore.models import Corpora, Document, Phrase

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    base_path = get_dir(os.path.join("export", "textual"))

    if import_type == "cor":
        # All Textual Data
        corpora = Corpora.objects.all()
        # create export directory
        cor_path = get_dir(os.path.join(base_path, "all_corpora"))
        path = get_dir(os.path.join(cor_path, current_time))
        for corpus in corpora:
            # create directory for each corpora
            corpus_path = get_dir(os.path.join(path, slugify(corpus.title)))
            export_documents(path=corpus_path, documents=corpus.documents.all())
            # create text files for each phrase collection inside corpora
            corpus_phrase_collection_path = get_dir(
                os.path.join(corpus_path, "phrase_collections")
            )
            export_phrase_collections(
                path=corpus_phrase_collection_path,
                collections=corpus.phrase_collections.all(),
            )
        zip_and_delete_dir(
            filename=current_time, root_dir=path, destination_path=cor_path
        )

    if import_type == "doc":
        # All Documents
        documents = Document.objects.all()
        # create text files for each document
        doc_path = get_dir(os.path.join(base_path, "all_documents"))
        path = get_dir(os.path.join(doc_path, current_time))
        export_documents(path=path, documents=documents)
        zip_and_delete_dir(
            filename=current_time, root_dir=path, destination_path=doc_path
        )

    if import_type == "phr":
        # All Phrases
        phrases = Phrase.objects.all()
        phr_path = get_dir(os.path.join(base_path, "all_phrases"))
        path = get_dir(os.path.join(base_path, current_time))
        file_path = os.path.join(path, current_time + ".csv")
        export_phrases(path=file_path, phrases=phrases)
        zip_and_delete_dir(
            filename=current_time, root_dir=path, destination_path=phr_path
        )


def export_ontological_data(ontology_domain, language):
    from datacore.models import Concept, Relation

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
    concepts = Concept.objects.filter(ontology_domain=ontology_domain)
    # create export directory
    base_path = get_dir(os.path.join("export", "conceptual"))
    path = get_dir(os.path.join(base_path, current_time))
    # export concepts, synonyms, and antonyms
    concept_path = os.path.join(path, "concepts.csv")
    with open(concept_path, "w", encoding="utf-8") as file:
        for concept in concepts:
            synonyms = ",".join(
                [item.text for item in concept.synonyms.filter(language=language).all()]
            )
            antonyms = ",".join(
                [item.text for item in concept.antonyms.filter(language=language).all()]
            )
            file.write(f"{concept.id}\t{concept.pos}\t{synonyms}\t{antonyms}\n")

    # export definitions
    definitions_path = os.path.join(path, "definitions.csv")
    with open(definitions_path, "w", encoding="utf-8") as file:
        for concept in concepts:
            definitions = "\t".join(
                [
                    item.text
                    for item in concept.definitions.filter(language=language).all()
                ]
            )
            file.write(f"{concept.id}\t{definitions}\n")

    # export definitions
    examples_path = os.path.join(path, "examples.csv")
    with open(examples_path, "w", encoding="utf-8") as file:
        for concept in concepts:
            examples = "\t".join(
                [item.text for item in concept.examples.filter(language=language).all()]
            )
            file.write(f"{concept.id}\t{examples}\n")

    # export relations
    relations = Relation.objects.all()  # filter(ontology_domain=ontology_domain)
    relation_path = os.path.join(path, "relation.csv")
    with open(relation_path, "w", encoding="utf-8") as file:
        for relation in relations:
            file.write(
                f"{relation.concepts[0]}\t{relation.concepts[1]}\t{relation.relation_type}\n"
            )

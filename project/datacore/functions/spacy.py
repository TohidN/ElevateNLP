# globally available Spacy NLP pipeline
def get_spacy(package="en_core_web_sm"):
    # use "package" as the dictionary key, so all following recalls evokes cached version of pipline in global variable
    global NLP
    try:
        NLP
    except NameError:
        NLP = {}
    try:
        NLP[package]
    except KeyError:
        import spacy

        NLP[package] = spacy.load(package)
    return NLP[package]


def spacy_document_tokenize(document, package="en_core_web_sm"):
    from datacore.functions.spacy import get_spacy
    from datacore.models import Phrase

    nlp = get_spacy(package=package)
    doc = nlp(document.content)
    # Clear document sentences
    Phrase.objects.filter(document=document).delete()
    document.phrases.clear()
    # Add each new sentence
    for sentence in doc.sents:
        phrase, created = Phrase.objects.get_or_create(
            text=sentence.text, document=document
        )
        if created and document.language:
            phrase.language = document.language
            phrase.save()
        document.phrases.add(phrase)


def spacy_phrase_analysis(
    phrase_item=None, sentence=None, language="en", package="en_core_web_sm"
):
    """
    Analyze a single phrase and save it
    sentence: cached sentence in case it's already generated
    phrase_item: reference to loaded phrase object, instead of loading it
    """
    from datacore.functions.spacy import get_spacy
    from datacore.functions.utils import strip_word
    from datacore.models import (Analyzer, Component, Language, NamedEntity,
                                 Phrase, PhraseAnalysis, Template, Word,
                                 WordRelation, WordRelationType)

    lemma_relation, created = WordRelationType.objects.get_or_create(
        title="Lemma",
        direction_type="d",
        descriptor="is the lemma of",
        reverse_descriptor="is a form of",
    )
    analyzer, created = Analyzer.objects.get_or_create(title=f"Spacy: {package}")
    language_item = Language.objects.get(alpha2=language)

    text = phrase_item.text
    # get or create spacy'z pipline object
    if sentence is None:
        nlp = get_spacy(package=package)
        phrase = nlp(text)
        if len(list(phrase.sents)) != 1:
            raise Exception(
                "Phrase analysis should only be called for a single phrase. use document analysis for multi-phrase texts."
            )
    else:
        phrase = sentence

    # analyze phrase
    data = {}
    data["words"] = {}
    data["ner"] = {}
    pos_template = []
    xpos_template = []
    feat_template = []
    dep_template = []

    analysis, created = PhraseAnalysis.objects.get_or_create(
        phrase=phrase_item, analyzer=analyzer
    )
    for token in phrase:
        word_text = strip_word(token.text).lower()
        word_id = str(token.i)
        # create word object
        word_obj, created = Word.objects.get_or_create(
            text=word_text, language=language_item
        )
        if created:
            word_obj.text_length = len(token.text)
        # add word to phrases words_list and if it's new add it to frequency distribution counter
        if word_text not in phrase_item.words_list:
            phrase_item.words_list.append(word_text)
            word_obj.frequency_distribution = word_obj.frequency_distribution + 1
        word_obj.save()
        analysis.words.add(word_obj)

        # word lemma
        if token.lemma_.lower() == word_text.lower():
            word_obj.lemma_frequency_distribution = (
                word_obj.lemma_frequency_distribution + 1
            )
        else:
            lemma_obj, created = Word.objects.get_or_create(
                text=token.lemma_, language=language_item
            )
            # add lemma to phrases lemmas_list and if it's new add it to frequency distribution counter
            if token.lemma_.lower() not in phrase_item.lemmas_list:
                phrase_item.lemmas_list.append(token.lemma_.lower())
                lemma_obj.lemma_frequency_distribution = (
                    lemma_obj.lemma_frequency_distribution + 1
                )
            lemma_obj.save()
            # add lemma as word's lemma using WordRelation: word_obj, lemma_obj
            lemma_rel, created = WordRelation.objects.get_or_create(
                words=[lemma_obj.id, word_obj.id], word_relation=lemma_relation
            )
        word_obj.save()
        analysis.words.add(word_obj)

        # create analysis data
        data["words"][word_id] = {}
        data["words"][word_id]["id"] = int(token.i)
        data["words"][word_id]["text"] = word_text
        data["words"][word_id]["lemma"] = token.lemma_
        data["words"][word_id]["upos"] = token.pos_
        data["words"][word_id]["xpos"] = token.tag_
        data["words"][word_id]["start_char"] = phrase[token.i : token.i + 1].start_char
        data["words"][word_id]["end_char"] = phrase[token.i : token.i + 1].end_char
        data["words"][word_id]["dep_rel"] = token.dep_
        data["words"][word_id]["dep_parent"] = token.head.i
        if token.morph is not None and str(token.morph) != "":
            word_feats = {}
            for feat in str(token.morph).split("|"):
                splited = feat.split("=")
                word_feats[splited[0]] = splited[1]
            data["words"][word_id]["feats"] = word_feats

        # template list items
        pos_template.append(token.pos_)
        xpos_template.append(
            "{}({})".format(token.pos_, token.tag_) if token.tag_ else token.pos_
        )
        feat_template.append("{}({}~{})".format(token.pos_, token.tag_, token.morph))
        dep_template.append(
            "({},{},{},{})".format(token.i, token.pos_, token.dep_, token.head.i)
        )

    # template list string
    pos_template = "-".join(pos_template)
    xpos_template = "-".join(xpos_template)
    feat_template = "-".join(feat_template) if feat_template is not None else ""
    dep_template = "-".join(dep_template)

    # Create Named Entities
    i = 0
    for item in phrase.ents:
        data["ner"][i] = {
            "text": item.text,
            "start_char": item.start_char,
            "end_char": item.end_char,
            "type": item.label_,
        }
        i = i + 1

    for item in phrase.ents:
        entity, created = NamedEntity.objects.get_or_create(
            text=item.text, ne_type=item.label_
        )

        if entity.text.lower() not in phrase_item.entities_list:
            phrase_item.entities_list.append(entity.text.lower())
            entity.frequency_distribution = entity.frequency_distribution + 1

        entity.save()
        analysis.entities.add(entity)

    # save phrase in case words, lemmas, and entities are updated
    phrase_item.save()

    # Create constituency template
    # TODO: Add constituency parser using "benepar": https://spacy.io/universe/project/self-attentive-parser

    # Create templates
    template_data = {}
    template_data["structure"] = {}
    for token in phrase:
        word_id = str(token.i)
        template_data["structure"][word_id] = {}
        template_data["structure"][word_id]["id"] = data["words"][word_id]["id"]
        template_data["structure"][word_id]["upos"] = data["words"][word_id]["upos"]
    template, created = Template.objects.get_or_create(
        pos=pos_template, parent=None, data=template_data
    )

    new_template, created = Template.objects.get_or_create(
        pos=pos_template,
        xpos=xpos_template,
        feats=feat_template,
        dep=dep_template,
        parent=template,
    )
    if created:
        for token in phrase:
            word_id = str(token.i)
            template_data["structure"][word_id]["xpos"] = data["words"][word_id]["xpos"]
            template_data["structure"][word_id]["dep_rel"] = data["words"][word_id][
                "dep_rel"
            ]
            template_data["structure"][word_id]["dep_parent"] = data["words"][word_id][
                "dep_parent"
            ]
        new_template.data = template_data
        new_template.phrase_type = (
            template.phrase_type if template.phrase_type else None
        )
        new_template.save()

    # store analysis data
    analysis.template = new_template
    analysis.data = data
    analysis.save()

    result = {"data": data, "ent": phrase.ents, "templates": {}}
    result["templates"]["pos_template"] = pos_template
    result["templates"]["xpos_template"] = xpos_template
    result["templates"]["feat_template"] = feat_template
    result["templates"]["dep_template"] = dep_template
    return result, analysis

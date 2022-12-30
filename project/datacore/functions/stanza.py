# globally available Stanza NLP pipeline
def get_stanza(lang="en", processors="tokenize,pos,lemma,depparse"):
    # create a key for NLP dic, so all following recalls evokes cached version of pipline in global variable
    # sorting processors prevents duplicate calls from equivalant list
    processors = ",".join(sorted([x for x in processors.split(",")]))
    key = "{}-{}".format(lang, processors)
    global NLP
    try:
        NLP
    except NameError:
        NLP = {}
    try:
        NLP[key]
    except KeyError:
        import stanza

        # NLP = stanza.Pipeline(lang=lang, processors=processors, use_gpu=True, batch_size=100, tokenize_batch_size = 32, pos_batch_size = 32, depparse_batch_size = 32)
        NLP[key] = stanza.Pipeline(lang=lang, processors=processors)
    return NLP[key]


def stanza_tokenize_document(document):
    """
    Process document by tokenizing it and storing it's sentences. sentences can be analyzed after tokenizing.
    params:
            document: document which will be tokenized
            analyze: if true, then pos, lemma depparse and named entity recognition will be performed on each sentence of it
    """
    from datacore.functions.stanza import get_stanza
    from datacore.models import Phrase

    nlp = get_stanza(lang="en", processors="tokenize")
    doc = nlp(document.content)
    # Clear document sentences
    Phrase.objects.filter(document=document).delete()
    document.phrases.clear()
    # Add each new sentence
    for sentence in doc.sentences:
        phrase, created = Phrase.objects.get_or_create(
            text=sentence.text, document=document
        )
        if created and document.language:
            phrase.language = document.language
            phrase.save()
        document.phrases.add(phrase)


def stanza_phrase_analysis(phrase_item=None, language="en", sentence=None):
    """
    Analyze a single phrase and save it
    sentence: cached sentence in case it's already generated
    phrase_item: reference to loaded phrase object, instead of loading it
    """

    from datacore.functions.stanza import get_stanza
    from datacore.functions.utils import strip_word
    from datacore.models import (
        Analyzer,
        Language,
        NamedEntity,
        PhraseAnalysis,
        Template,
        Word,
        WordRelation,
        WordRelationType,
    )

    # TODO: cache this three lines
    lemma_relation, created = WordRelationType.objects.get_or_create(
        title="Lemma",
        direction_type="d",
        descriptor="is the lemma of",
        reverse_descriptor="is a form of",
    )
    analyzer, created = Analyzer.objects.get_or_create(title="Stanza")
    language_item = Language.objects.get(alpha2=language)

    text = phrase_item.text
    # get or create stanza's sentence object
    if sentence is None:
        # TODO: seperate "processor" into list, search for available pipelines to only perform tasks which are available.
        nlp = get_stanza(
            lang="en", processors="tokenize,pos,lemma,depparse,ner,constituency"
        )
        doc = nlp(text)
        if len(doc.sentences) != 1:
            raise Exception(
                "Phrase analysis should only be called for a single phrase. use document analysis for multi-phrase texts."
            )
        phrase = doc.sentences[0]
    else:
        phrase = sentence

    # analyze phrase
    data = {}
    data["words"] = {}
    data["ner"] = {}
    pos_template = []
    xpos_template = []
    feat_template = []

    analysis, created = PhraseAnalysis.objects.get_or_create(
        phrase=phrase_item, analyzer=analyzer
    )
    for word in phrase.words:
        word_text = strip_word(word.text).lower()
        word_id = str(word.id - 1)
        # create word object
        word_obj, created = Word.objects.get_or_create(
            text=word_text, language=language_item
        )
        if created:
            word_obj.text_length = len(word.text)
        # add word to phrases words_list and if it's new add it to frequency distribution counter
        if word_text not in phrase_item.words_list:
            phrase_item.words_list.append(word_text)
            word_obj.frequency_distribution = word_obj.frequency_distribution + 1

        # word lemma
        if word.lemma.lower() == word_text.lower():
            word_obj.lemma_frequency_distribution = (
                word_obj.lemma_frequency_distribution + 1
            )
        else:
            lemma_obj, created = Word.objects.get_or_create(
                text=word.lemma, language=language_item
            )
            # add lemma to phrases lemmas_list and if it's new add it to frequency distribution counter
            if word.lemma.lower() not in phrase_item.lemmas_list:
                phrase_item.lemmas_list.append(word.lemma.lower())
                lemma_obj.lemma_frequency_distribution = (
                    word_obj.lemma_frequency_distribution + 1
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
        data["words"][word_id]["id"] = word.id - 1
        data["words"][word_id]["text"] = word_text
        data["words"][word_id]["lemma"] = word.lemma
        data["words"][word_id]["upos"] = word.upos
        data["words"][word_id]["xpos"] = word.xpos
        data["words"][word_id]["start_char"] = word.start_char
        data["words"][word_id]["end_char"] = word.end_char

        if word.feats is not None:
            word_feats = {}
            for feat in str(word.feats).split("|"):
                splited = feat.split("=")
                word_feats[splited[0]] = splited[1]
            data["words"][word_id]["feats"] = word_feats

        # template list items
        pos_template.append(word.pos)
        xpos_template.append(
            "{}({})".format(word.pos, word.xpos) if word.xpos else word.pos
        )
        feat_template.append("{}({}~{})".format(word.pos, word.xpos, word.feats))
    # template list string
    pos_template = "-".join(pos_template)
    xpos_template = "-".join(xpos_template)
    feat_template = "-".join(feat_template) if feat_template is not None else ""

    # Create dependency template
    dep_list = []
    for dep in phrase.dependencies:
        dep_list.append(
            "({},{},{},{})".format(
                dep[2].id - 1, dep[2].pos, dep[2].deprel, dep[0].id - 1
            )
        )
        data["words"][str(dep[2].id - 1)]["dep_rel"] = dep[2].deprel
        data["words"][str(dep[2].id - 1)]["dep_parent"] = (
            dep[0].id - 1 if dep[0].id > 0 else 0
        )
    dep_template = "-".join(dep_list)

    # Create Named Entities
    data["ner"] = {}
    i = 0
    for item in phrase.ents:
        data["ner"][i] = {
            "text": item.text,
            "start_char": item.start_char,
            "end_char": item.end_char,
            "type": item.type,
        }
        i = i + 1

        entity, created = NamedEntity.objects.get_or_create(
            text=item.text, ne_type=item.type.upper()
        )

        if entity.text.lower() not in phrase_item.entities_list:
            phrase_item.entities_list.append(entity.text.lower())
            entity.frequency_distribution = entity.frequency_distribution + 1

        entity.save()
        analysis.entities.add(entity)

    # save phrase in case words, lemmas, and entities are updated
    phrase_item.save()

    # Create constituency template
    def get_constituency_template(children):
        result = ""
        c = 0
        for child in children:
            c = c + 1
            if len(child.children) > 0:
                result = result + child.label
                if len(child.children[0].children):
                    result = (
                        result + "(" + get_constituency_template(child.children) + ")"
                    )
                elif c != len(children):
                    result = result + ","
        return result

    constiruancy_template = get_constituency_template(phrase.constituency.children)
    # Create templates
    template_data = {}
    template_data["structure"] = {}
    for word in phrase.words:
        word_id = str(word.id - 1)
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
        constituency=constiruancy_template,
        parent=template,
    )
    if created:
        for word in phrase.words:
            word_id = str(word.id - 1)
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
    result["templates"]["constiruancy"] = constiruancy_template
    return result, analysis

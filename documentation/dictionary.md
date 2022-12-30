
# Dictionary
**Ontology:** It encompasses a collection of cognitive entities belonging to one, more, or all domains and is formally defined by it's categories, properties, and relations between other concepts and entities.

**Ontology learning:** automatic or semi-automatic creation of ontologies, including extracting a domain's terms from natural language text.

**Domain:** A subject area. can be general or specific to a single subject.

**Instance(Object, Individual, Named Entity):** it is derived from ontology classes(Concept) and inherits its properties.
> Instance data model is named Instance. however NamedEntity data model is created to store entities discovered in NER until they are defined as ontology instances.

**Concept(sets, collections, class, type):** A cognitive entity(concept) or a representation of specific kinds of things in the world(class, type). In some NLP tasks it's also called **Synset**, as it's represented with a ***Set of Synonyms***.

**Attribute( Aspect, Features, Characteristic):** each concept is best formally described by a set of attributes which are inherited by their instances and values for each given attribute.
attributes consist of:

 1. Concept or Instance
 2. Property
 3. Value: another concept or variable defined in specific data type

 E.g.
>  concept(Apple)
>> has property("has_color") => value(concept:red, concept:green)
>> has property("weight_in_gram") => range(50,250)
>> has property("is_edible") => value(true)

**Property:** custom defined data which describes a possible aspect of concept or object in *Attribute*.
E.g. has_color, weight_in_gram

**Relations:**  ways in which classes and *Instances* can be related to one another.
> Relations are predefined. E.g. hyponym(a kind of), meronym(part of),  has attribute, is caused by, etc

**Function terms:** complex structures formed from certain relations that can be used in place of an individual term in a statement.

**Restrictions:** formally stated descriptions of what must be true in order for some assertion to be accepted as input.

**Rules:**:    statements in the form of an if-then (antecedent-consequent) sentence that describe the logical inferences that can be drawn from an assertion in a particular form.

**Axioms:** assertions (including rules) in a logical form that together comprise the overall theory that the ontology describes in its domain of application. This definition differs from that of "axioms" in generative grammar and formal logic. In these disciplines, axioms include only statements asserted as a priori knowledge. As used here, "axioms" also include the theory derived from axiomatic statements.

**Events:** the changing of attributes or relations.

**Actions:** types of events

ElevateNLP is a web-based NLP Platform for the creation, organization, management, and visualization of natural language data for performing NLP Tasks. Several NLP frameworks (E.g. Stanza, Spacy, Etc) are already implemented in this platform. Elevate NLP is accessible via its responsive and progressive frontend, Restful-API, or Jupyter Notebooks with access to Django ORM.

# Features:
* Create and manage corpora, by adding documents and phrase collections to them with frontend UI or create imports using python or iPython notebooks.
* Create and manage domain ontologies.
* Build linguistic components as you need or use standard and treebank compatible linguistic components available.
* Easily perform NLP task on text(available frameworks include Stanza, Spacy, NLTK)
* View visualization of ontologies
* Analyze corpora, documents, phrases, and phrase collections using available NLP pipelines.
* Collaborate with other users to extend your corpora or domain ontology
* Export linguistic, textual, or ontological data.
* Built-in Restful-API access.
* Easy import data with available examples including the following datasets:
	* Squad2: A corpora and documents and questions for each document
	* Tatoeba: Multi-language and linked phrases.
	* Import proverbs, idioms, expressions and sayings: Scrapped and import task
	* WordNet: Import wordnet as general domain ontology.
* Examples of most tasks are available in iPython notebooks.
* Rapid application development using Django
* Responsive frontend powered by [Bootstrap](getbootstrap.com/) and developed as a Progressive Web Apps (PWAs) powered by [HTMX](https://htmx.org/).
* Created with the idea of language independence and compatibility with standard tree-banks
* All relevant data can be tagged and filtered with language and data source identifiers.

# Getting Started
1. Install the platform according to [the installation guide](documentation/installation.md).
2. Access the web or API interface by opening its URL in the browser.
3. Access Jupyter Notebooks by running notebook server commands.

You can use available tools(web-based interface, API, or notebooks) to perform the following tasks.
* Create a corpus, add documents, and phrase collections to it.
* Create a document, and add phrase collections to it. E.g. questions, highlights, ...
* Analyze documents: Tokenization, lemmatization, POS, dependency and constituency parsing, ...
* Create phrase collections with linked phrases for tasks such as machine translation, question answering, and chatbots, ...
* Create ontologies, with their linguistic(synonym, antonym, definition, example), and notological data(concept, properties, relations, axioms, etc)
* Visualize ontology relations in graphs.
* Analyze data to get word and sentence pattern usage frequency.
* Filter and sort words based on usage frequency, length, or it's composition.
* Manage available languages list and linguistic components or create your own.
* Manage data sources, and their references and filter their data.
* Export textual, lexical, or ontological data.

# Some Use Cases
I've used This framework for the following tasks:
* As a framework to manage and edit raw data for language models(used in NLU)
* As a frontend for creating data artifacts for Ontology Learning tasks(for my master's thesis)
* As a database accessible with Django ORM for performing NLP workflow tasks such as natural language pre-processing, statistical analysis of large corpora, and linguistic analysis workflows.
* As a tool for linguistic pattern recognition, visualization, and reporting.
* I've also created a language learning app for my personal use which generates usage frequency for words and sentence patterns from an imported german corpus, then generates meaningful phrases as quiz data based on the combination of usage frequency and syntax complexity.

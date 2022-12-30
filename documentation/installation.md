# Installation Guide
## Setup Environment
1.  Create a Virtual Environment and activate to it.
2. Switch to `documentation/requirements/` and install dependencies using requirements files.
```shell
pip install -r "requirements.ver.dev.txt"
```
Requirement files include:
* **requirements.txt:**  full requierments for development environment.
* **requirements.dev.txt**: list of requirements for development environment, without package versions.
* **requirements.ver.dev.txt**: list of requirements for development environment, including package versions.
* **requirements.prod.txt**: version list of requirements for production environment, without package versions..
* **requirements.prod.txt**: version list of requirements for development environment, including package versions..
## Setup Database
1. install and configure PostgreSQL.
2. Install 'citext' extension for your database on psql prompt:
```shell
psql =# \c db_1
CREATE EXTENSION citext;
```
This allows NoSQL fields such as json and array fields which this project uses.
3. edit `.env` file in `project/` directory to reflect your database configuration. I.e. database credentials.
## Creating database schema
Run the following commands to create database tables:
```shell
python .\manage.py makemigrations
python .\manage.py migrate
```
## Import languages and linguistic components
Run following commands to import linguistics components and languages data:
```shell
python .\manage.py import-linguistics
python .\manage.py import-languages
```
This will populate linguistic compenent's table, as well as list of languages used to tag data.
## Setup NLP frameworks
Run setup command or manually add download required language models for your NLP tasks:
```shell
python .\manage.py setup:
```
This command currently includes installation of default english language resources for NLP frameworks Stanza, NLTK, and Spacy. to change NLP frameworks language models, create a copy of `project/datacore/management/commands/setup.py` with a name such as `setup-fr.py` and change it's parameters or write your own code. then you can call new setup file with last parameter changed to reflect your filename. E.g. `python .\manage.py setup-fr`
## Run Server
### Web Server
To run web server, execute following command:
```shell
python .\manage.py runserver
```
This will run your web and API server. on successfull execution, the site will be available on `http://127.0.0.1:8000/` and APIs can be accessed via `http://127.0.0.1:8000/api`.
### Notebooks
To run Jupyter notebooks, switch to notebooks directory and execute following command.
```shell
cd ./notebooks
call python ../project/manage.py shell_plus --notebook
```

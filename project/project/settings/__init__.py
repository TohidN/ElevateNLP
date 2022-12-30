# Load module based on `.env` variable.
# this code mimmics `from module import *` with `module` being `SETTINGS_ENVIRONMENT` variable
from importlib import import_module

from decouple import config

module_name = config("SETTINGS_ENVIRONMENT", ".development")
module = import_module(module_name)
module_dict = module.__dict__
try:
    to_import = module.__all__
except AttributeError:
    to_import = [name for name in module_dict if not name.startswith("_")]
globals().update({name: module_dict[name] for name in to_import})

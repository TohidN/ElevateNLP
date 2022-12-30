from django import template
from django.template.defaulttags import register

register = template.Library()


@register.filter
def concept_title(id):
    from datacore.models import Concept

    concept = Concept.objects.get(id=id)
    return concept.get_title()


@register.simple_tag
def get_method_from_list(dic_list, key, method_name):
    from inspect import ismethod

    function = getattr(dic_list[key], method_name)
    return function() if ismethod(function) else function


@register.simple_tag
def in_relation(item, relation, search):
    # check to see if an item is in a manytomany relationship
    m = getattr(item, relation)
    if search in m.all():
        return True
    else:
        return False


@register.simple_tag
def get_item(mylist, key):
    return mylist[key]


@register.inclusion_tag("pagination.html")
def pagination(query, paginator_range, parameters=""):
    return {
        "query": query,
        "paginator_range": paginator_range,
        "parameters": parameters,
    }


@register.inclusion_tag("tabs.html")
def tabs(tabs, tab_active):
    return {
        "tabs": tabs,
        "tab_active": tab_active,
    }


@register.simple_tag
def file_or_default(filepath, default_path):
    from django.core.files.storage import default_storage

    if filepath and default_storage.exists(filepath):
        return filepath
    else:
        return default_path


@register.simple_tag
def url_or_default(filepath, default_path):
    from django.core.files.storage import default_storage

    if filepath and default_storage.exists(filepath):
        return default_storage.url(filepath)
    else:
        return default_storage.url(default_path)

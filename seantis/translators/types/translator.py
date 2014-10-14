from plone.directives import form
from seantis.people.types.base import PersonBase


class ITranslator(form.Schema):
    form.model("translator.xml")


class Translator(PersonBase):
    pass

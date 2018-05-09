from graphene import ObjectType, Schema, String
from textProcessing.app import addNLPTagsToPlainText


class Query(ObjectType):
    xmlFromNLP = String(text=String(default_value=""))

    def resolve_xmlFromNLP(self, info, text):
        return ' '.join(addNLPTagsToPlainText(text))

schema = Schema(query=Query)
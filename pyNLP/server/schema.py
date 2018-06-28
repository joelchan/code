from graphene import ObjectType, Schema, String, List
from textProcessing.app import addNLPTagsToPlainText #todo move this


class Query(ObjectType):
    xmlFromNLP = String(text=String(default_value=""))

    def resolve_xmlFromNLP(self, info, text):
        joinedSents = ' '.join(addNLPTagsToPlainText(text))
        return f"<p>{joinedSents}</p>"

schema = Schema(query=Query)
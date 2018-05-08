from graphene import ObjectType, Schema, String
from textProcessing.app import addNLPTagsToPlainText as addNLPTags


class Query(ObjectType):
    hello = String(name=String(default_value="yo"))

    def resolve_hello(self, info, name):
        return addNLPTags(name)

schema = Schema(query=Query)
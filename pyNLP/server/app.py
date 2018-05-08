import sys
sys.path.extend(
    ['E:\\code\\pyNLP',
     'E:\\code\\pyNLP\\server',
     'E:\\code\\pyNLP\\textProcessing'
     ])

from flask import Flask
from flask_graphql import GraphQLView
from schema import schema
app = Flask(__name__)
app.debug = True

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     # db_session.remove()

if __name__ == '__main__':
    app.run()
import sys, os
from pathlib import Path
thisFilesDir = os.path.dirname(os.path.realpath(__file__))
upDir = Path(thisFilesDir).parent
import platform

sys.path.extend(
    [str(upDir),
     str(upDir / 'server'),
     str(upDir / 'textProcessing')
     ])

from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS

from schema import schema
app = Flask(__name__)
CORS(app)
app.debug = True

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=False))

if __name__ == '__main__':
    print(platform.system())
    if (platform.system() == 'Windows'):
        app.run()
    else:
        app.run(host= '0.0.0.0') #windows needs admin for this, linux won't port map otherwise.
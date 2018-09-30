import random
#import dicttoxml
from flask import Flask, Response
from flask_restful import reqparse, abort, Api, Resource

from db import *

def MakeXML(eventsList):
    ret = "<markers>"
    for event in eventsList:
        ret += "<marker"
        for key in event.keys():
            ret += ' {0}="{1}"'.format(key, event[key])
        ret += "/>\n"
    ret += "</markers>"
    return ret 
    

app = Flask(__name__)
api = Api(app)

EXECUTE = {
    'empty': {'text': 'empty'},
}

def abort_if_todo_doesnt_exist(execute_id):
    if execute_id not in EXECUTE:
        abort(404, message="Todo {} doesn't exist".format(execute_id))

parser = reqparse.RequestParser()
parser.add_argument('lat')
parser.add_argument('lon')

class Execute(Resource):
    def get(self):
        args = parser.parse_args()
        lat, lon = args['lat'], args['lon']

        #distance in meters
        eventsList = getLocalEvents(lat, lon, 100000)
        
        xml = MakeXML(eventsList)
        #print(xml)
        r = Response(response=xml, status=201, mimetype="application/xml")
        r.headers["Content-Type"] = "text/xml; charset=utf-8"
        r.headers["Access-Control-Allow-Origin"] = '*'
        return r
        """
        return {'status': status,
                'events': events
                }, 201, {'Access-Control-Allow-Origin': '*'}"""

    def post(self):
        return EXECUTE

api.add_resource(Execute, '/execute')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5008,  threaded=True)

from flask import Flask, redirect
from flask.ext.restful import reqparse, abort, Api, Resource, fields,marshal_with
from flask_restful_swagger import swagger
import csv
import json
from google.cloud import datastore

app = Flask(__name__, static_folder='../static')

api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='Supplies summary statistics for Flaredown data')

def create_client():
    project_id = 'flaredown-149515'
    return datastore.Client(project_id)

def getCountsByCondition(client, trackable_type, condition):
    query = client.query(kind='Condition' + trackable_type)
    query.add_filter('condition','=',condition)
    for result in query.fetch(limit=1):
        return result

def getTotal(client, trackable_type, trackable_name):
    query = client.query(kind=trackable_type + 'Count')
    query.add_filter('name','=',trackable_name)
    for result in query.fetch(limit=1):
        return result['count']

def getAllTotals(client, trackable_type):
    query = client.query(kind=trackable_type + 'Count')
    totals_dict = {}
    for result in query.fetch():
        if result['name'] != 'condition':
            totals_dict[result['name']] = result['count']
    return totals_dict

def getConditionList(client):
    query = client.query(kind='ConditionList')
    conditions = []
    for result in query.fetch():
        conditions.append(result['name'])
    return conditions

class ConditionsList(Resource):
  @swagger.operation(
      notes='Returns a comma seperated list of all conditions.  Rather than a list of all conditions that have ever been reported, this is a currated list where synonymous conditions have been combined.  Where the other endpoints request a condition, it should be provided in the format given here.',
      nickname='get'
      )
  def get(self):
    client = create_client()
    conditions = getConditionList(client)

    return str(conditions), 200

class ConditionTrackableCounts(Resource):
  @swagger.operation(
      notes='Get the number of users that that report both a condition, and trackables of a certain type.  For example if you request Symptom/Fibromyalgia, you will be returned a list of how many people with Fibromyalgia also reported each symptom',
      nickname='get',
      parameters=[
          {
            "name": "condition",
            "description": "The name of the condition",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          },
          {
              "name": "trackable_type",
              "description": "The trackable type that the condition will be compared to (Condition, Symptom, Treatment, Tag)",
              "required": True,
              "allowMultiple": False,
              "dataType": 'string',
              "paramType": "path"
          }
      ])
  def get(self, trackable_type, condition):
    client = create_client()
    condition_dict = getCountsByCondition(client, trackable_type, condition)
    condition_dict.pop('condition', None)
    condition_dict.pop('id', None)
    if len(condition_dict.values()) == 0:
        return "condition not found", 404
    return json.dumps(condition_dict), 200

class ConditionTrackableCountsNormalized(Resource):
  @swagger.operation(
      notes='Get the percent of users that report a trackable and also reported a condition.  Used to estimate if a trackable is likely caused by a condition.  For example if you request Symptom/Fibromyalgia, you will be returned a list of what percentage of people reporting each symptom also reported Fibromyalgia.',
      nickname='get',
      parameters=[
          {
            "name": "condition",
            "description": "The name of the condition",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          },
          {
              "name": "trackable_type",
              "description": "The trackable type that the condition will be compared to (Condition, Symptom, Treatment, Tag)",
              "required": True,
              "allowMultiple": False,
              "dataType": 'string',
              "paramType": "path"
          }
      ])
  def get(self, trackable_type, condition):
    client = create_client()
    condition_dict = getCountsByCondition(client, trackable_type, condition)
    totals_dict = getAllTotals(client,trackable_type)

    condition_dict.pop('condition',None)
    condition_dict.pop('id', None)

    for key,value in condition_dict.iteritems():
        condition_dict[key] = float(value) / float(totals_dict[key])

    if len(condition_dict.values()) == 0:
        return "condition not found", 404
    return json.dumps(condition_dict), 200

class Counts(Resource):
  @swagger.operation(
      notes='Get the total number of users reporting a trackable',
      nickname='get',
      parameters=[
          {
              "name": "trackable_type",
              "description": "The type of the trackable, (Symptom, Condition, Treatment, Tag)",
              "required": True,
              "allowMultiple": False,
              "dataType": 'string',
              "paramType": "path"
          },
          {
              "name": "trackable_name",
              "description": "The name of the trackable",
              "required": True,
              "allowMultiple": False,
              "dataType": 'string',
              "paramType": "path"
          }
      ])
  def get(self, trackable_type, trackable_name):
      client = create_client()

      total = getTotal(client, trackable_type, trackable_name)
      return total, 200

##
## Actually setup the Api resource routing here
##
api.add_resource(ConditionsList,'/conditions')
api.add_resource(ConditionTrackableCounts, '/condition_counts/<string:trackable_type>/<string:condition>')
api.add_resource(ConditionTrackableCountsNormalized, '/condition_counts_norm/<string:trackable_type>/<string:condition>')
api.add_resource(Counts, '/counts/<string:trackable_type>/<string:trackable_name>')


@app.route('/docs')
def docs():
  return redirect('/static/docs.html')


if __name__ == '__main__':
  app.run(debug=True)
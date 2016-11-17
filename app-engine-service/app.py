from flask import Flask, redirect
from flask.ext.restful import reqparse, abort, Api, Resource, fields,marshal_with
from flask_restful_swagger import swagger
import csv
import json

app = Flask(__name__, static_folder='../static')

###################################
# This is important:
api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/api/spec',
                   description='Supplies summary statistics for Flaredown data')
###################################

def getSymptomsByCondition(condition):
    condition_dict = {}
    with open('Symptom_count_by_condition.csv', 'rt') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print row['Condition']
            if row['Condition'].lower() == condition.lower():
                condition_dict = row
    condition_dict.pop('', None)
    condition_dict.pop('Condition', None)
    return condition_dict

def getSymptomTotals():
    totals = {}
    infile = open('Symptom_counts.csv')
    for line in infile:
        symptom,count = line.split(',')
        totals[symptom] = count
    return totals

class ConditionsList(Resource):
  @swagger.operation(
      notes='Returns a comma seperated list of all conditions.',
      nickname='get'
      )
  def get(self):
    conditions = []
    reader = csv.reader(open('Symptom_count_by_condition.csv'))
    for row in reader:
        conditions.append(row[0])

    return str(conditions), 200

class Symptoms(Resource):
  @swagger.operation(
      notes='Get the number of users that that suffer from a condition and each symptom',
      nickname='get',
      parameters=[
          {
            "name": "condition",
            "description": "The name of the condition",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          }
      ])
  def get(self, condition):
    condition_dict = getSymptomsByCondition(condition)
    if len(condition_dict.values()) == 0:
        return "condition not found", 404
    return json.dumps(condition_dict), 200

class NormalSymptoms(Resource):
  @swagger.operation(
      notes='Get the percentage of a users that report a symptom that also report the supplied condition.  Used to estimate how likely it is that a symptom is being cause by a condition',
      nickname='get',
      parameters=[
          {
              "name": "condition",
              "description": "The name of the condition",
              "required": True,
              "allowMultiple": False,
              "dataType": 'string',
              "paramType": "path"
          }
      ])
  def get(self, condition):
      totals_dict = getSymptomTotals()
      condition_dict = getSymptomsByCondition(condition)
      for symptom, count in condition_dict.iteritems():
          condition_dict[symptom] = float(count) / float(totals_dict[symptom])
      if len(condition_dict.values()) == 0:
          return "condition not found", 404
      return json.dumps(condition_dict), 200

##
## Actually setup the Api resource routing here
##
api.add_resource(ConditionsList,'/conditions')
api.add_resource(Symptoms, '/symptoms/<string:condition>')
api.add_resource(NormalSymptoms, '/symptoms_normal/<string:condition>')


@app.route('/docs')
def docs():
  return redirect('/static/docs.html')


if __name__ == '__main__':
  app.run(debug=True)
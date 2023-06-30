#!/usr/bin/python3
# run file: python ./cost_per_agent.py -c C4SOC.ini

import json, requests, time
from elasticsearch import Elasticsearch, helpers
import configparser, argparse

from datetime import date, datetime #Receive the date
from pytz import timezone #Change the date and time to zulu time

import pymsteams

myTeamsMessage = pymsteams.connectorcard("https://rcssecure.webhook.office.com/webhookb2/14ad0430-9425-4ea4-97de-685bd16f0b00@d5f3726c-43b1-4fdc-b850-fcc377f78ef0/IncomingWebhook/a94b187badc84a7c85f805cbeafc4288/90e46ffc-a2bc-4587-9310-a5d9b981f4fc")
newline = "\n\n"

def finding_the_cost_per_agent():

  nameSpace = ""
  module_name = "TWI getCliCount"

  string_data = ""

  __version__ = "0.0.1"

  def get_parser(h):
      parser = argparse.ArgumentParser(add_help=h)
      parser.add_argument('-c','--config', help='Configuration file used to connect to Elastic', required=True)
      return parser

  def client_namespace(startTime, endTime, authKey, apiReq):
      clinamespace = {}
      clientData = {
        "query": {
          "bool": {
            "must": [
              {
                "range": {
                  "@timestamp": {
                    "gte": startTime,
                    "lte": endTime,
                    "format": "strict_date_optional_time"
                  }
                }
              }
            ]
          }
        },
        "size": 10000,
        "aggs" : { "distinct_values" : { "terms" : { "field" : "data_stream.namespace" , "size": 10000 } } }
      }


      clinamespace = requests.post(
          apiReq, json=clientData,
          headers={'Authorization': authKey},
      )

      tmp_NS = clinamespace.json()

      return tmp_NS




  def client_counts(startTime, endTime, nameSpace, authKey, apiReq):
      cliCount = {}
      clientData = {
        "query": {
          "bool": {
            "must": [
              {
                "range": {
                  "@timestamp": {
                    "gte": startTime,
                    "lte": endTime,
                    "format": "strict_date_optional_time"
                  }
                }
              },
              { "match": {"data_stream.namespace": nameSpace } }
            ]
          }
        },
        "size": 10000,
        "aggs": { "distinct_hosts": {"cardinality": {"field": "agent.id"} } }
      }


      cliCnt = requests.post(
          apiReq, json=clientData,
          headers={'Authorization': authKey},
      )

      tmp_cli = cliCnt.json()

      return tmp_cli


  if __name__ == "__main__":

    p = get_parser(h=True)
    args = p.parse_args()
    config = configparser.ConfigParser()

    config.read('C4SOC.ini')
    authKey=config.get('BILLING', 'authKey')
    #startTime = config.get('BILLING', 'startTime')
    #endTime = config.get('BILLING', 'endTime')

    current_date = date.today()
    str_current_date = str(current_date)

    startTime = str_current_date + "T" + "00:00:00.000" + "Z"
    endTime = str_current_date + "T" + "23:59:59.000" + "Z"

    apiReq = config.get('BILLING', 'billEndpoint')


  cliNSList = client_namespace(startTime, endTime, authKey, apiReq)
  cnt = len(cliNSList["aggregations"]["distinct_values"]["buckets"])

  number_of_namespaces = "There are: "+str(cnt)+" Namespaces in this cluster.\n--------------------------\n"
  print(number_of_namespaces)

  customer_agents_time_range = "Customer/Agents from: "+startTime+" - "+endTime + newline
  print(customer_agents_time_range)
  print("Client,Agents")

  

  string_data = string_data + number_of_namespaces + str(customer_agents_time_range) + newline

  


  total_agents = 0 #declared new variable to find sum of total agents
  for client in cliNSList["aggregations"]["distinct_values"]["buckets"]:
      locnt = 0
      for key, value in client.items():
        if locnt % 2 == 0:
            cliAgentCnt = client_counts(startTime, endTime, value, authKey, apiReq)
            clientName = str(value)
            agentCount = str(cliAgentCnt["aggregations"]["distinct_hosts"]["value"])
            print(clientName+","+agentCount)

            #new_line = "\n--------------------------\n"
            string_data = string_data + clientName + ": " + agentCount + newline

            

            int_agent_count = int(agentCount)
            # Total Agents
            total_agents = total_agents + int_agent_count
            str_total_agents = str(total_agents)
        else:
            eventCount = str(value)
        locnt=locnt+1

  print("Total agents: " + str_total_agents)
  print("")
  print("")
  string_data = string_data + " Total Agents: " + str_total_agents + newline + newline

  # Finding the Costs
  print("Calculating Platform Costs")

  string_data = string_data + "Calculating Platform Costs" + "\n--------------------------\n"

  ecAPI_Key = "cEkzM1FJVUJmLTRqbnktV1hIcmI6YW1meTVUcllSdEc4SG82a2YxMXhwdw=="
  orgID = "3257624349"
  deployID = "8a6ca552a69044899689ba80ff42c1ec"

  current_date = date.today()
  str_current_date = str(current_date)
  startTime = str_current_date + "T00:00:00.000Z"
  endTime = str_current_date + "T23:59:59.000Z"

  tdict = {'0763d762158c40349fe9ac8a2185ae15':'Driven Brands', '8a6ca552a69044899689ba80ff42c1ec':'Velocity', 'b22c2908209046d28736e6a7c7334db7':'Meijer', 'f0a317f1ef144972ba2080bf004b4ea5':'WineDirect','51ef0f4ae3c149508e03953f6efe9237':'C4-SOC'} #, 'bb79df0e676449ddba1b497f78cb59c4':'C4-Admin'}

  total_platform_cost = 0 #new variable to receive total cost

  for x in tdict:
      dep = tdict[x]
      req = "https://api.elastic-cloud.com/api/v1/billing/costs/"+orgID+"/deployments/"+x+"/items?from="+startTime+"&to="+endTime
      indxList=[]

      print(str(x)+" -- "+str(dep))
      string_data = string_data + str(x) + ": " + str(dep) + newline

      platform_time_range = "Time Period - Beginning: "+startTime+" and Ending: "+endTime
      print(platform_time_range)
      string_data = string_data + platform_time_range + newline

      response = requests.get(
          req,
          headers={'Authorization': 'ApiKey cEkzM1FJVUJmLTRqbnktV1hIcmI6YW1meTVUcllSdEc4SG82a2YxMXhwdw=='},
      )

      json_response = response.json()

      costs = []
      rtype = []
      storeCost = 0.0

      for item in json_response['costs']['dimensions']:
          costs.append(item['cost'])
          rtype.append(item['type'])

      #print(costs)
      print("------------------------------------------------")
      individual_platform_str_cost = str(round(json_response["costs"]["total"],2))

      total_monthly_cost_statement = "\tTotal Monthly Cost for "+dep+" was "+ individual_platform_str_cost + newline
      print(total_monthly_cost_statement) #Total Cost
      string_data = string_data + total_monthly_cost_statement + newline

      platform_cost = float(individual_platform_str_cost)
      total_platform_cost = total_platform_cost + platform_cost


      myService = str(rtype[0])
      myCost = str(round(costs[0],2))

      additional_storage_costs_statements = "\tCost for "+myService+": was "+myCost+" plus these additional storage costs:"
      print(additional_storage_costs_statements)
      string_data = string_data + additional_storage_costs_statements + newline


  # Fix this
      for l in [1,2,3,4,5]:
          json_response_dimension_type = "\t"+str(json_response["costs"]["dimensions"][l]["type"])
          json_response_dimension_cost =  str(round(json_response["costs"]["dimensions"][l]["cost"],2))
          print(json_response_dimension_type+" --- "+json_response_dimension_cost)

          string_data = string_data + json_response_dimension_type + ": " + json_response_dimension_cost + newline

          storeCost += json_response["costs"]["dimensions"][l]["cost"]

      print("\t-----------------------------------------------------")

      last_storage_costs_statement = "\tStorage Costs: "+str(round(storeCost,2))
      print(last_storage_costs_statement)
      string_data = string_data + last_storage_costs_statement + newline
      print("\n")


      awsDataName = []
      awsDataActual = []
      awsDataFormatted = []

      for item in json_response['data_transfer_and_storage']:
          awsDataName.append(item['name'])

      awsDataInName0 = str(json_response["data_transfer_and_storage"][0]["name"])
      awsDataInActual0 = str(json_response["data_transfer_and_storage"][0]["quantity"]["value"])
      awsDataInFormatted0 = str(json_response["data_transfer_and_storage"][0]["quantity"]["formatted_value"])

      awsDataXferInternodeName = str(json_response["data_transfer_and_storage"][1]["name"])
      awsDataXferInternodeActual = str(json_response["data_transfer_and_storage"][1]["quantity"]["value"])
      awsDataXferInternodeFormatted = str(json_response["data_transfer_and_storage"][1]["quantity"]["formatted_value"])




      awsDataXferOutName = str(json_response["data_transfer_and_storage"][2]["name"])
      awsDataXferOutActual = str(json_response["data_transfer_and_storage"][2]["quantity"]["value"])
      awsDataXferOutFormatted = str(json_response["data_transfer_and_storage"][2]["quantity"]["formatted_value"])


      awsDataStorageAPIName = str(json_response["data_transfer_and_storage"][3]["name"])
      awsDataStorageAPIActual = str(json_response["data_transfer_and_storage"][3]["quantity"]["value"])
      awsDataStorageAPIFormatted = str(json_response["data_transfer_and_storage"][3]["quantity"]["formatted_value"])




      awsDataSnapshotStorage = str(json_response["data_transfer_and_storage"][4]["name"])
      awsDataSnapshotStorageActual = str(json_response["data_transfer_and_storage"][4]["quantity"]["value"])
      awsDataSnapshotStorageFormatted = str(json_response["data_transfer_and_storage"][4]["quantity"]["formatted_value"])



      data_transfer_and_storage_volume_statement = "\tData Transfer and Storage Volumes for the Time Period"
      print(data_transfer_and_storage_volume_statement)
      string_data = string_data + data_transfer_and_storage_volume_statement + newline

      string_data = string_data + "\t-----------------------------------------------------" + newline

      aws_data_transfer_in = "\t"+awsDataInName0+" Actual was: "+awsDataInActual0+", Formatted Value:"+awsDataInFormatted0
      print(aws_data_transfer_in)
      string_data = string_data + aws_data_transfer_in + newline

      aws_data_transfer_internode = "\t"+awsDataXferInternodeName+" Actual was: "+awsDataXferInternodeActual+", Formatted Value:"+awsDataXferInternodeFormatted
      print(aws_data_transfer_internode)
      string_data = string_data + aws_data_transfer_internode + newline

      aws_data_transfer_out = "\t"+awsDataXferOutName+" Actual was: "+awsDataXferOutActual+", Formatted Value:"+awsDataXferOutFormatted
      print(aws_data_transfer_out)
      string_data = string_data + aws_data_transfer_out + newline

      aws_snapshot_storage_api = "\t"+awsDataStorageAPIName+" Actual was: "+awsDataStorageAPIActual+", Formatted Value:"+awsDataStorageAPIFormatted
      print(aws_snapshot_storage_api)
      string_data = string_data + aws_snapshot_storage_api + newline

      aws_snapshot_storage = "\t"+awsDataSnapshotStorage+" Actual was: "+awsDataSnapshotStorageActual+", Formatted Value:"+awsDataSnapshotStorageFormatted
      print(aws_snapshot_storage_api)
      string_data = string_data + aws_snapshot_storage + newline

      string_data = string_data + "------------------------------------------------\n" + newline

  str_total_platform_cost = str(total_platform_cost)
  total_platform_cost_statement = "Total_platform_cost: $" + str_total_platform_cost
  print(total_platform_cost_statement)
  string_data = string_data + total_platform_cost_statement + newline

  print("Calculating Cost per Agent" + newline)
  cost_per_agent = total_platform_cost / total_agents
  str_cost_per_agent = str(cost_per_agent)

  str_cost_per_agent_statement = "The cost per agent on average is $" + str_cost_per_agent

  print(str_cost_per_agent_statement)

  string_data = string_data + str_cost_per_agent_statement + newline

  the_message = myTeamsMessage.text(string_data)
  return myTeamsMessage.send()

print(finding_the_cost_per_agent())

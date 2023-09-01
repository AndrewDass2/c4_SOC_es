#!/usr/bin/python3
# run file: "python ./c4_SOC_es.py -c C4SOC.ini", module_name = "TWI getCliCount", __version__ = "0.0.1"

import json, requests, configparser, argparse, pymsteams, datetime, check_the_date, day_number
from elasticsearch import Elasticsearch, helpers

config = configparser.ConfigParser()
config.read('C4SOC.ini')
myTeamsMessage = pymsteams.connectorcard(config.get('MSTEAMS','mswebhook'))
newline = "\n\n"

yesterday_date = check_the_date.date()
today_year_number, today_month_number = day_number_and_zulu_time.day_ztime_info()[0], day_number_and_zulu_time.day_ztime_info()[1]
today_day_number = day_number_and_zulu_time.day_ztime_info()[2]

total_cost_throughout_month = {}

for i in range(int(yesterday_date[2]), int(yesterday_date[2]) + 1): #int(yesterday_date[2])
  def finding_the_cost_per_agent():
    nameSpace = ""
    teams_string_data = ''
    active_namespaces = "{"
    client_agent_dictionary = {}
    day_in_the_month = yesterday_date[1] + "/" + str(i)

    def get_parser(h):
        parser = argparse.ArgumentParser(add_help=h)
        parser.add_argument('-c','--config', help='Configuration file used to connect to Elastic', required=True)
        return parser

    def connect_elasticsearch(): # Connect to ES
      _es = Elasticsearch(api_key=config['ELASTIC']['enkey'], cloud_id=config['ELASTIC']['cloud_id'])

      if _es.ping():
          print('Connected to Elasticsearch')
      else:
          print('Unable to connect to Elasticsearch')
      return _es

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

    def index_info_to_es():
      information_to_send_to_es = {
        "starttime": startTime,
        "endtime": endTime,
        "current_day": yesterday_date[1] + '/' + str(i) + '/' + yesterday_date[0],
        "@timestamp": datetime.datetime.now(),
        "number_of_namespaces": cnt,
        "active_namespaces": active_namespaces,
        "agents": client_agent_dictionary,
        "total_agents": total_agents,
        "cost_for_capacity": float(myCost),
        "cost_stats": {
          "total_daily_cost": individual_platform_cost,
          "data_in": round(json_response["costs"]["dimensions"][1]["cost"],2),
          "data_internode": round(json_response["costs"]["dimensions"][2]["cost"],2),
          "data_out": round(json_response["costs"]["dimensions"][3]["cost"],2),
          "storage_api": round(json_response["costs"]["dimensions"][4]["cost"],2),
          "storage_bytes": round(json_response["costs"]["dimensions"][5]["cost"],2),
          "storage_costs": round(storeCost,2),
          "data_in_actual": float(awsDataInActual0),
          "data_in_formatted": str(awsDataInFormatted0),
          "data_internode_actual": float(awsDataXferInternodeActual),
          "data_internode_formatted": str(awsDataXferInternodeFormatted),
          "data_transfer_out_actual": float(awsDataXferOutActual),
          "data_transfer_out_formatted": str(awsDataXferOutFormatted),
          "snapshot_storage_api_actual": float(awsDataStorageAPIActual),
          "snapshot_storage_api_formatted": str(awsDataStorageAPIFormatted),
          "snapshot_storage_actual": float(awsDataSnapshotStorageActual),
          "snapshot_storage_formatted": str(awsDataSnapshotStorageFormatted)},
        "total_platform_cost":total_platform_cost,
        "average_agent_cost": float(str_cost_per_agent)
    }
      return information_to_send_to_es

    if __name__ == "__main__":
      p = get_parser(h=True)
      args = p.parse_args()
      authKey=config.get('BILLING', 'authKey')

      es=connect_elasticsearch()

      if i <= 9:
        startTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + "0" + str(i) + "T" + "00:00:00.000" + "Z"
        endTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + "0" + str(i) + "T" + "23:59:59.000" + "Z"
      else:
        startTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + str(i) + "T" + "00:00:00.000" + "Z"
        endTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + str(i) + "T" + "23:59:59.000" + "Z"

      apiReq = config.get('BILLING', 'billEndpoint')

    cliNSList = client_namespace(startTime, endTime, authKey, apiReq)
    cnt = len(cliNSList["aggregations"]["distinct_values"]["buckets"])

    number_of_namespaces = "There are: "+str(cnt)+" Namespaces in this cluster.\n--------------------------\n"
    customer_agents_time_range = '"' + 'Customer/Agents from' + '" ' + ': ' + '"' +startTime+' - '+endTime + '"' + newline
    teams_string_data = teams_string_data + number_of_namespaces + str(customer_agents_time_range) + newline

    total_agents = 0
    for client in cliNSList["aggregations"]["distinct_values"]["buckets"]:
        locnt = 0
        for key, value in client.items():
          if locnt % 2 == 0:
              cliAgentCnt = client_counts(startTime, endTime, value, authKey, apiReq)
              clientName = str(value)
              agentCount = str(cliAgentCnt["aggregations"]["distinct_hosts"]["value"])

              add_to_active_namespaces = '"' + clientName + '"' + ':' + '"' + agentCount + '",' + '\n'
              active_namespaces = active_namespaces + add_to_active_namespaces

              int_agent_count = int(agentCount)
              client_agent_dictionary[clientName] = int_agent_count

              total_agents = total_agents + int_agent_count
              str_total_agents = str(total_agents)
          else:
              eventCount = str(value)
          locnt=locnt+1

    active_namespaces = active_namespaces[0:len(active_namespaces) - 2] + '}'

    teams_string_data = teams_string_data + active_namespaces + newline
    teams_string_data = teams_string_data + 'Total Agents' + ' : ' + str_total_agents + newline + newline
    teams_string_data = teams_string_data + "\n------------------------------------------------\n" + newline

    # Costs
    teams_string_data = teams_string_data + "Calculating Platform Costs" + "\n--------------------------\n"
    orgID = config.get('BILLING','orgID')
    bill_url = config.get('BILLING', 'billing_cost_url')

    if i <= 9:
      startTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + "0" + str(i) + "T" + "00:00:00.000" + "Z"
      endTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + "0" + str(i) + "T" + "23:59:59.000" + "Z"
    else:
      startTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + str(i) + "T" + "00:00:00.000" + "Z"
      endTime = yesterday_date[0] + "-" + yesterday_date[1] + "-" + str(i) + "T" + "23:59:59.000" + "Z"

    code, name = config.get('TDICT','code'), config.get('TDICT','name')
    tdict = {code:name}
    total_platform_cost = 0

    for x in tdict:
        dep = tdict[x]
        req = bill_url+orgID+"/deployments/"+x+"/items?from="+startTime+"&to="+endTime
        indxList=[]

        teams_string_data = teams_string_data + '"' + str(x) + '"' + ' : ' + str(dep) + newline
        platform_time_range_beginning = str(dep) + ' Time Period - Beginning' + ' : ' + startTime
        platform_time_range_ending = str(dep) + ' Time Period - Ending' + ' : ' + endTime
        teams_string_data = teams_string_data + platform_time_range_beginning + newline + platform_time_range_ending + newline

        billkey = config.get('ELASTIC','billkey')
        response = requests.get(
            req,
            headers={'Authorization': billkey},
        )

        json_response = response.json()
        costs, rtype = [], []
        storeCost = 0.0

        for item in json_response['costs']['dimensions']:
            costs.append(item['cost'])
            rtype.append(item['type'])

        individual_platform_cost = round(json_response["costs"]["total"],2)
        individual_platform_str_cost = str(individual_platform_cost)
        total_monthly_cost_statement =  str(dep) + ' Total Monthly Cost for '+dep+' was ' + ' : ' + individual_platform_str_cost + newline
        teams_string_data = teams_string_data + total_monthly_cost_statement + newline

        platform_cost = float(individual_platform_str_cost)
        total_platform_cost = total_platform_cost + platform_cost

        myService = str(rtype[0])
        myCost = str(round(costs[0],2))

        additional_storage_costs_statements =  str(dep) + ' Cost for '+str(myService) + ' : ' + str(myCost)
        teams_string_data = teams_string_data + additional_storage_costs_statements + newline

        for l in [1,2,3,4,5]:
            json_response_dimension_type = str(json_response["costs"]["dimensions"][l]["type"])
            json_response_dimension_cost =  str(round(json_response["costs"]["dimensions"][l]["cost"],2))
            storeCost += json_response["costs"]["dimensions"][l]["cost"]
            teams_string_data = teams_string_data + str(dep) + " " + json_response_dimension_type + " : " + json_response_dimension_cost + newline

        last_storage_costs_statement = str(dep) + ' Storage Costs' + ' : ' + str(round(storeCost,2))
        teams_string_data = teams_string_data + last_storage_costs_statement + newline

        awsDataName = []

        for item in json_response['data_transfer_and_storage']:
            awsDataName.append(item['name'])

        awsDataInName0, awsDataInActual0, awsDataInFormatted0 = str(json_response["data_transfer_and_storage"][0]["name"]), str(json_response["data_transfer_and_storage"][0]["quantity"]["value"]), str(json_response["data_transfer_and_storage"][0]["quantity"]["formatted_value"])
        awsDataXferInternodeName, awsDataXferInternodeActual, awsDataXferInternodeFormatted = str(json_response["data_transfer_and_storage"][1]["name"]), str(json_response["data_transfer_and_storage"][1]["quantity"]["value"]), str(json_response["data_transfer_and_storage"][1]["quantity"]["formatted_value"])
        awsDataXferOutName, awsDataXferOutActual, awsDataXferOutFormatted = str(json_response["data_transfer_and_storage"][2]["name"]), str(json_response["data_transfer_and_storage"][2]["quantity"]["value"]), str(json_response["data_transfer_and_storage"][2]["quantity"]["formatted_value"])
        awsDataStorageAPIName, awsDataStorageAPIActual, awsDataStorageAPIFormatted = str(json_response["data_transfer_and_storage"][3]["name"]), str(json_response["data_transfer_and_storage"][3]["quantity"]["value"]), str(json_response["data_transfer_and_storage"][3]["quantity"]["formatted_value"])
        awsDataSnapshotStorage, awsDataSnapshotStorageActual, awsDataSnapshotStorageFormatted = str(json_response["data_transfer_and_storage"][4]["name"]), str(json_response["data_transfer_and_storage"][4]["quantity"]["value"]), str(json_response["data_transfer_and_storage"][4]["quantity"]["formatted_value"])

        aws_data_transfer_in = str(dep) + ' ' + awsDataInName0 + ' Actual was' + ' : ' + awsDataInActual0 + ',' + ' Formatted Value' + ' : ' + awsDataInFormatted0
        teams_string_data = teams_string_data + aws_data_transfer_in + newline

        aws_data_transfer_internode = str(dep) + ' ' + awsDataXferInternodeName + ' Actual was' + ' : ' + awsDataXferInternodeActual + ',' + ' Formatted Value' + ' : ' + awsDataXferInternodeFormatted
        teams_string_data = teams_string_data + aws_data_transfer_internode + newline

        aws_data_transfer_out = str(dep) + ' ' + awsDataXferOutName + ' Actual was ' + ': ' + awsDataXferOutActual + ',' + ' Formatted Value' + ' : ' + awsDataXferOutFormatted
        teams_string_data = teams_string_data + aws_data_transfer_out + newline

        aws_snapshot_storage_api = str(dep) + ' ' + awsDataStorageAPIName + ' Actual was' + ' : ' + awsDataStorageAPIActual + ', Formatted Value : ' + awsDataStorageAPIFormatted
        teams_string_data = teams_string_data + aws_snapshot_storage_api + newline

        aws_snapshot_storage =  str(dep) + ' ' + awsDataSnapshotStorage + ' Actual was' + ' : ' + awsDataSnapshotStorageActual + ', Formatted Value : ' + awsDataSnapshotStorageFormatted
        teams_string_data = teams_string_data + aws_snapshot_storage + newline

        teams_string_data = teams_string_data + "\t-----------------------------------------------------" + newline

    teams_string_data = teams_string_data + "Costs" + "\n--------------------------\n"
    str_total_platform_cost = str(total_platform_cost)
    total_platform_cost_statement = 'Total_platform_cost' + ' : ' + '$' + str_total_platform_cost
    teams_string_data = teams_string_data + total_platform_cost_statement + newline

    cost_per_agent = total_platform_cost / total_agents
    str_cost_per_agent = str(cost_per_agent)
    str_cost_per_agent_statement = 'The cost per agent on average is ' + ': ' + '$' + str_cost_per_agent
    teams_string_data = teams_string_data + str_cost_per_agent_statement + newline

    if i <= 9:
      #es.indices.create(index=str_current_date_month + "_" + str_current_date_year) #don't have to run this line to recreate if it was already created beforehand
      es.index(
          index='c4_soc_'+ yesterday_date[1] + "_" + yesterday_date[0],
          id='c4_soc_' + "0"+str(i),
          document=index_info_to_es()
      )
    else:
      #es.indices.create(index=str_current_date_month + "_" + str_current_date_year + "_dashboard") #don't have to run this line to recreate if it was already created beforehand
      es.index(
          index='c4_soc_' + yesterday_date[1] + "_" + yesterday_date[0],
          id='c4_soc_' + str(i),
          document=index_info_to_es()
      )

    # print(teams_string_data)
    the_teams_message = myTeamsMessage.text(teams_string_data)
    return myTeamsMessage.send()

  finding_the_cost_per_agent()

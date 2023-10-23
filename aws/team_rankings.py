import json
import traceback
import ratings_module as module

'''
Python 3 Boilerplate for AWS Lambda Proxy Integration
https://github.com/donnieprakoso/boilerplate-aws-lambda-proxy-python3

This boilerplate refers to AWS documentation, link as below:
http://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-set-up-simple-proxy.html#api-gateway-simple-proxy-for-lambda-input-format
'''

'''
Request JSON format for proxy integration
{
  "resource": "Resource path",
  "path": "Path parameter",
  "httpMethod": "Incoming request's method name"
  "headers": {Incoming request headers}
  "queryStringParameters": {query string parameters }
  "pathParameters":  {path parameters}
  "stageVariables": {Applicable stage variables}
  "requestContext": {Request context, including authorizer-returned key-value pairs}
  "body": "A JSON string of the request payload."
  "isBase64Encoded": "A boolean flag to indicate if the applicable request payload is Base64-encode"
}


Response JSON format
{
  "isBase64Encoded": true|false,
  "statusCode": httpStatusCode,
  "headers": { "headerName": "headerValue", ... },
  "body": "..."
}

'''

def response_proxy(data):
  '''
  For HTTP status codes, you can take a look at https://httpstatuses.com/
  '''
  response = {}
  response["isBase64Encoded"] = False
  response["statusCode"] = 200
  response["headers"] = {}
  response["body"] = json.dumps(data)
  return response


def response_no_team_ids():
  response = response_proxy(None)
  response["body"] = {
    "message": "No team ids!"
  }
  return response

# Local Testing: python-lambda-local -f handler -t 5 team_rankings.py event.json
# API query must look like team_ids=98926509885559666&team_ids=98767991877340524&team_ids=98767991892579754&team_ids=98767991853197861
# OR team_ids=98926509885559666,98767991877340524,98767991892579754,98767991853197861
def handler(event, context):
  print("REQUEST: ------------------------------")
  print(event)
  response = response_proxy(None)

  try:

    if "team_ids" not in event['multiValueQueryStringParameters']:
      response = response_no_team_ids()
      return response

    # Get event tournament id and stage
    team_ids = event['multiValueQueryStringParameters']['team_ids']

    if len(team_ids) == 1:
      team_ids = team_ids[0].split(",")

    if len(team_ids) == 0:
      response = response_no_team_ids()
      return response

    # Get rating info
    ratings = module.handler_team_rankings(team_ids)


    response = response_proxy(list(ratings.values()))

  except Exception as e:
    traceback.print_exc()
    response["statusCode"] = 400
    response["body"] = {
      "message": "ERROR occurred :("
    }   
  
  print("RESPONSE: ------------------------------")
  print(response)
  return response



'''
Response body
{"request_data": "{'resource': '/tournament_rankings/{tournament_id+}', 
'path': '/tournament_rankings/lol_tournament_test', 'httpMethod': 'GET', 
'headers': None, 'multiValueHeaders': None, 'queryStringParameters': {'stage': 'worlds'}, 
'multiValueQueryStringParameters': {'stage': ['worlds']}, 
'pathParameters': {'tournament_id': 'lol_tournament_test'}, 
'stageVariables': None, 'requestContext': {'resourceId': 'l0rczj', 'resourcePath': 
'/tournament_rankings/{tournament_id+}', 'httpMethod': 'GET', 'extendedRequestId': 'NKxSdEJNvHcFc0Q=', 'requestTime': '21/Oct/2023:20:06:26 +0000', 'path': '/tournament_rankings/{tournament_id+}', 'accountId': '356161843961', 'protocol': 'HTTP/1.1', 'stage': 'test-invoke-stage', 'domainPrefix': 'testPrefix', 'requestTimeEpoch': 1697918786687, 'requestId': 'ebcee54e-7937-4b37-944d-ab9a27ba66b3', 'identity': {'cognitoIdentityPoolId': None, 'cognitoIdentityId': None, 'apiKey': 'test-invoke-api-key', 'principalOrgId': None, 'cognitoAuthenticationType': None, 'userArn': 'arn:aws:iam::356161843961:root', 'apiKeyId': 'test-invoke-api-key-id', 'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36', 'accountId': '356161843961', 'caller': '356161843961', 'sourceIp': 'test-invoke-source-ip', 'accessKey': 'ASIAVF3HGOL4W65R6UDR', 'cognitoAuthenticationProvider': None, 'user': '356161843961'}, 'domainName': 'testPrefix.testDomainName', 'apiId': 'mqb2k0rcn5'}, 'body': None, 'isBase64Encoded': False}"}
'''
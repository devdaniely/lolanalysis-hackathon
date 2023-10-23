import json
import traceback


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


def response_bad_num_teams():
  response = response_proxy(None)
  response["body"] = {
    "message": "number_of_teams must be a positive integer!"
  }
  return response

# Local Testing: python-lambda-local -f handler -t 5 global_rankings.py event.json
def handler(event, context):
  response = response_proxy(None)
  print("REQUEST: ------------------------------")
  print(event)

  try:
    # Default to 20
    num_teams = 20

    # Get number of teams
    if event["queryStringParameters"] != None and "number_of_teams" in event["queryStringParameters"]:
      parsed_num = int(event["queryStringParameters"]["number_of_teams"])
      if parsed_num > 0:
        num_teams = parsed_num

    # Get rating info
    with open("global_data.json", "r") as json_file:
      rating_data = json.load(json_file)

    ratings_list = list(rating_data.values())
    team_count = 0

    ratings = []
    while team_count < num_teams and team_count < len(ratings_list):
      ratings.append(ratings_list[team_count])
      team_count += 1

    response = response_proxy(ratings)

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
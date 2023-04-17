import json
import boto3
import os
import urllib.parse

SES = boto3.client('ses')
EMAIL_SUBJECT = os.environ['EMAIL_SUBJECT']

email_from = "no-reply@cloudbuilders.io"

with open('data.txt') as f:
    EMAIL_BODY = f.read()

with open('data1.txt') as f:
    EMAIL_BODY1 = f.read()

with open('welcome_body.txt') as f:
    EMAIL_BODY_WELCOME = f.read()

def lambda_handler(event, context):
    try:
        print(event)
        sqs_message = event['Records'][0]['body']
        print(sqs_message)
        body = json.loads(sqs_message)
        email_to = body['Business Email']
        name = body['Full Name']
        type = body['Type']
        print(sqs_message)
        print(body)
        print(email_to, name,type)


        url = "https://cbx.mycloudbuilders.com/verify/"
        data = {"Full Name": name, "Business Email": email_to}
        query_params = urllib.parse.urlencode({"body": json.dumps(data)}, quote_via=urllib.parse.quote)
        link = url + "?" + query_params


        print(link)

    except KeyError as e:
        error_message = f'Missing required parameter: {str(e)}'
        print(error_message)
        return {
            'statusCode': 400,
            'body': json.dumps({'error': error_message})
        }

    try:
        if type == 'POST':
            email_text = f"Dear {name},{EMAIL_BODY}{link}{EMAIL_BODY1}"
            response = SES.send_email(
                Source=email_from,
                Destination={
                    'ToAddresses': [email_to]
                },
                Message={
                    'Subject': {
                        'Data': EMAIL_SUBJECT
                    },
                    'Body': {
                        'Text': {
                            'Data': email_text
                        }
                    }
                }
            )
        elif type == 'PUT' :
            
            email_text2 = f"Dear {name},\n{EMAIL_BODY_WELCOME}"
            response = SES.send_email(
                Source=email_from,
                Destination={
                    'ToAddresses': [email_to]
                },
                Message={
                    'Subject': {
                        'Data': "Welcome to Cloud Managed care plan by CloudBuilders "
                    },
                    'Body': {
                        'Text': {
                            'Data': email_text2
                        }
                    }
                }
            )

    except Exception as e:
        error_message = f'Failed to send email: {str(e)}'
        print(error_message)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': error_message})
        }

    return {
        'statusCode': 200,
        'body': json.dumps({'messageId': response['MessageId']})
    }

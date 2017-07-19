"""Self-Signed

Create a Self-Signed request for an AWS service.

See the AWS documentation here:
    http://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-authenticating-requests.html?shortFooter=true

1. Create a Canonical Request
2. Create a String to Sign
3. Calculate the Signature
4. Add the Signing Information to the Request
5. Conduct the API call

"""


import os
import sys
import json
import hmac
import hashlib
import datetime
import boto3
import requests
from botocore.exceptions import ProfileNotFound


# These parameters should remain static
ALGORITHM = 'AWS4-HMAC-SHA256'
CONTENT_TYPE = 'application/json'
TIME = datetime.datetime.utcnow()
AMZ_DATE = TIME.strftime('%Y%m%dT%H%M%SZ')
DATE_STAMP = TIME.strftime('%Y%m%d')


# Set these parameters for your API call
METHOD = 'GET'
SERVICE = 'es'
REGION = 'us-west-2'
ENDPOINT = 'search-ancestry-streaming-poc-yjhotcsza2y6n5zij6opeed3gm.us-west-2.es.amazonaws.com'
PROFILE = 'training'
PAYLOAD = {
    "query" : {
        "bool": {
            "must": [{
                "range": {
                    "@timestamp": {
                        "gte": "1-d/d",
                        "lt": "now"
                    }
                }
            }]
        }
    }
}


try:
    SESSION       = boto3.session.Session(profile_name=PROFILE)
    CREDS         = SESSION.get_credentials()
    ACCESS_KEY    = CREDS.access_key
    SECRET_KEY    = CREDS.secret_key
    SESSION_TOKEN = CREDS.token
except ProfileNotFound as pnf:
    SESSION       = boto3.session.Session()
    ACCESS_KEY    = os.environ.get('AWS_ACCESS_KEY_ID')
    SECRET_KEY    = os.environ.get('AWS_SECRET_ACCESS_KEY')
    SESSION_TOKEN = os.environ.get('AWS_SESSION_TOKEN')


if ACCESS_KEY is None or SECRET_KEY is None:
    print 'No access key is available.'
    sys.exit()


def create_canonical_req():
    """Step 1. Create a canonical request
    """
    uri = '/_search'
    querystring = ''
    headers = 'content-type;host;x-amz-date'
    hashed_payload = payload_hash(PAYLOAD)
    canonical_request = "\n".join([
        METHOD,
        uri,
        querystring,
        str('content-type:' + CONTENT_TYPE),
        str('host:' + ENDPOINT),
        str('x-amz-date:' + AMZ_DATE),
        "",
        headers,
        hashed_payload
    ])

    return canonical_request


def payload_hash(payload):
    """Create a hash of the submitted payload
    """
    new_payload = hashlib.sha256(json.dumps(payload)).hexdigest()

    return new_payload


def create_credential_scope():
    """Create the credential scope for this request
    """
    scope = "/".join([
        DATE_STAMP,
        REGION,
        SERVICE,
        'aws4_request'
    ])

    return scope


def create_string_to_sign(cred_scope, can_request):
    """Step 2. Create the string to be sent in the request
    """
    string_to_sign = "\n".join([
        ALGORITHM,
        AMZ_DATE,
        cred_scope,
        hashlib.sha256(can_request).hexdigest()
    ])

    return string_to_sign


def calculate_signature(string2sign):
    """Step 3. Calculate a signature for the payload
    """
    signing_key = get_signature_key(SECRET_KEY, DATE_STAMP, REGION, SERVICE)
    signature = hmac.new(signing_key, (string2sign).encode('utf-8'), hashlib.sha256).hexdigest()

    return signature


def create_authorization_header(cred_scope, signature):
    """Create the authorization header for the request
    """
    authorization_header = ALGORITHM + \
                       ' Credential=' + \
                       ACCESS_KEY + '/' + \
                       cred_scope + ', ' + \
                       'SignedHeaders=content-type;host;x-amz-date, ' + \
                       'Signature=' + signature

    return authorization_header


def create_signed_headers(auth_header):
    """Create the signed headers for the request
    """
    headers = {
        'Content-Type': CONTENT_TYPE,
        'Host': ENDPOINT,
        'Content-Length': utf8len(json.dumps(PAYLOAD)),
        'X-Amz-Security-Token': SESSION_TOKEN,
        'X-Amz-Date': AMZ_DATE,
        'Authorization': auth_header
    }

    return headers


def utf8len(string):
    """From AWS documentation

    Get the number of bytes in a string
    """

    return bytes(len(string.encode('utf-8')))


def sign(key, msg):
    """From AWS documentation

    Create a cryptographic hash object
    """

    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()


def get_signature_key(key, date_stamp, region, service):
    """From AWS documentation

    Create a hashed key for the request
    """
    k_date = sign(('AWS4' + key).encode('utf-8'), date_stamp)
    k_region = sign(k_date, region)
    k_service = sign(k_region, service)
    k_signing = sign(k_service, 'aws4_request')

    return k_signing


def build_headers():
    """Step 4. Add the Signing Information to the Request
    """
    canon          = create_canonical_req()
    creds          = create_credential_scope()
    string_to_sign = create_string_to_sign(cred_scope=creds,
                                           can_request=canon)
    sig            = calculate_signature(string_to_sign)
    authorization  = create_authorization_header(cred_scope=creds,
                                                 signature=sig)
    headers        = create_signed_headers(auth_header=authorization)

    return headers


def execute_api_call(signed_header):
    """Step 5. Conduct the API call
    """
    es_host = ENDPOINT
    search = '/_search'
    method_string = 'http://' + es_host + search
    body = json.dumps(PAYLOAD)
    print(method_string)
    req = requests.get(
        method_string,
        data=body,
        headers=signed_header
    )

    return req


def lambda_handler(event, context):
    """Lambda Handler for Self-Signed
    """
    head = build_headers()
    response = execute_api_call(head)
    print response.text


if __name__ == '__main__':
    lambda_handler({}, {})

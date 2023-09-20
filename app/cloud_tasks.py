import json
import os

from google.cloud import tasks_v2beta3

client = tasks_v2beta3.CloudTasksClient()

PROJECT_NAME = os.environ.get("GOOGLE_PROJECT_NAME", "Glyph Development")
QUEUE_REGION = os.environ.get("QUEUE_REGION", "us-central1")
QUEUE_ID = os.environ.get("QUEUE_ID", "file-processing")


def send_task(url, http_method='POST', payload=None):
    """ Send task to be executed """

    # construct the queue
    parent = client.queue_path(PROJECT_NAME,
                               QUEUE_REGION, queue=QUEUE_ID)

    # construct the request body
    task = {
        'app_engine_http_request': {
            'http_method': http_method,
            'relative_uri': url
        }
    }

    if isinstance(payload, dict):
        # convert dict to JSON string
        payload = json.dumps(payload)

    if payload is not None:
        # The API expects a payload of type bytes
        converted_payload = payload.encode()

        # Add the payload to the request body
        task['app_engine_http_request']['body'] = converted_payload

    # use the client to build and send the task
    response = client.create_task(parent=parent, task=task)

    return response

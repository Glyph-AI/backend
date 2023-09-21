import json
import os

from google.cloud import tasks_v2

client = tasks_v2.CloudTasksClient()

PROJECT_NAME = os.environ.get("GOOGLE_PROJECT_NAME", "Glyph Development")
QUEUE_REGION = os.environ.get("QUEUE_REGION", "us-central1")
QUEUE_ID = os.environ.get("QUEUE_ID", "file-processing")
TARGET_BASE_URL = os.environ.get(
    "WORKER_URL", "https://glyph-worker-52f2ltqu7q-uc.a.run.app")


def send_task(url, http_method='POST', payload=None):
    """ Send task to be executed """

    if isinstance(payload, dict):
        # convert dict to JSON string
        payload = json.dumps(payload)

    if payload is not None:
        # The API expects a payload of type bytes
        converted_payload = payload.encode()

    task = tasks_v2.Task(
        http_request=tasks_v2.HttpRequest(
            http_method=tasks_v2.HttpMethod.POST,
            url=f"{TARGET_BASE_URL}{url}",
            body=converted_payload
        )
    )

    # construct the queue
    parent = client.queue_path(PROJECT_NAME,
                               QUEUE_REGION, queue=QUEUE_ID)

    # use the client to build and send the task
    response = client.create_task(parent=parent, task=task)

    return response

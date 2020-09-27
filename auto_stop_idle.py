#!/usr/bin/env python3

import http.client
import os
import ssl
import json
from datetime import datetime
import boto3


def get_instance_name():
    log_path = "/opt/ml/metadata/resource-metadata.json"
    with open(log_path, "r") as logs:
        _logs = json.load(logs)
    return _logs["ResourceName"]


def is_kernel_idle(kernel, path):
    if kernel["execution_state"] == "idle":
        last_activity = datetime.strptime(
            kernel["last_activity"], "%Y-%m-%dT%H:%M:%S.%fz"
        )
        idle_time = (datetime.utcnow() - last_activity).total_seconds()
        if idle_time > idle_timeout:
            print(f"Kernel {kernel['id']} ({kernel['name']}) for {path} is idle")
            return True

    return False


def check_instance_uptime():
    last_modified = sagemaker_client.describe_notebook_instance(
        NotebookInstanceName=instance_name
    )["LastModifiedTime"]
    return (datetime.now(last_modified.tzinfo) - last_modified).total_seconds()


def shutdown_instance():
    print("Shutting down idle notebook.")
    sagemaker_client.stop_notebook_instance(NotebookInstanceName=instance_name)


jupyter_host = os.getenv("SAGEMAKER_JUPYTER_HOST", "localhost")
jupyter_port = int(os.getenv("SAGEMAKER_JUPYTER_PORT", "8888"))
jupyter_ssl = os.getenv("SAGEMAKER_JUPYTER_SECURE", "false") == "true"
idle_timeout = int(os.getenv("SAGEMAKER_JUPYER_IDLE_TIME", "3600"))
idle_shutdown = os.getenv("SAGEMAKER_JUPYER_IDLE_SHUTDOWN", "false") == "true"

instance_name = (
    os.getenv("SAGEMAKER_INSTANCE_NAME")
    if "SAGEMAKER_INSTANCE_NAME" in os.environ
    else get_instance_name()
)

conn = (
    http.client.HTTPSConnection(
        jupyter_host, jupyter_port, timeout=10, context=ssl._create_unverified_context()
    )
    if jupyter_ssl
    else http.client.HTTPConnection(jupyter_host, jupyter_port, timeout=10)
)

try:

    conn.request("GET", "/api/sessions")

    sessions_response = conn.getresponse()

    data = json.loads(sessions_response.read().decode("utf-8"))

    is_idle = False

    sagemaker_client = boto3.client("sagemaker")

    if len(data) == 0:
        is_idle = True
    else:
        all_idle_status = [
            is_kernel_idle(session["kernel"], session["path"]) for session in data
        ]
        instance_uptime = check_instance_uptime()
        instance_idle = instance_uptime > idle_timeout
        all_idle_status.append(instance_idle)
        is_idle = all(all_idle_status)

    print(f"Notebook instance idle status: {is_idle}.")

    if is_idle and idle_shutdown:
        shutdown_instance()
finally:
    conn.close()


#!/usr/bin/env python3

import argparse
import json
import subprocess
import sys

# Install boto3 if not already installed
subprocess.check_call([sys.executable, "-m", "pip", "install", "boto3"])

import boto3  # noqa


def invoke(args):
    client = boto3.client("lambda", region_name="us-west-1")

    # Your Lambda function name
    fn_name = f"django-neon-{args.env}-{args.name}"

    command_args = [args.command]

    if args.params:
        params = args.params.split(" ")
        command_args += params

    payload = {"_wsgi": {"command": "manage", "args": command_args}}
    invocation_type = "RequestResponse"

    print("Invoking command in AWS Lambda...")
    print(f"{fn_name}$ ./manage.py {' '.join(command_args)}")

    invoke_response = client.invoke(
        FunctionName=fn_name,
        InvocationType=invocation_type,
        Payload=bytes(json.dumps(payload), "utf-8"),
    )

    print(json.dumps(invoke_response, indent=4, sort_keys=True, default=str))

    if "FunctionError" in invoke_response:
        raise Exception("Failed Invoke")

    print(json.load(invoke_response["Payload"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Execute manage.py commands in a specified env and Lambda."
    )
    parser.add_argument(
        "env",
        choices=[
            "prod",
            "dev",
        ],
        help="Execution environment",
    )
    parser.add_argument(
        "name",
        choices=[
            "api",
        ],
        help="Name of the Lambda to run in.",
    )
    parser.add_argument(
        "command", type=str, help="Name of the management command to execute."
    )
    parser.add_argument(
        "-p",
        "--params",
        type=str,
        help="Additional parameters for management command quoted.",
    )
    parser.set_defaults(function=invoke)

    args = parser.parse_args()
    args.function(args)

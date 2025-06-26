#!/usr/bin/env python3
import os
import aws_cdk as cdk

from synapse_status.synapse_status_stack import SynapseStatusStack


def get_required_env(key: str) -> str:
  value = os.environ.get(key)
  if value is None:
    raise ValueError(f"Missing environment variable: {key}")
  return value

app = cdk.App()
SynapseStatusStack(app, "SynapseStatusStack",
                   env = cdk.Environment(account=cdk.Aws.ACCOUNT_ID, region="us-east-1"),
                   statuspage_api_key = get_required_env("statuspage_api_key"),
                   statuspage_page_id = get_required_env("statuspage_page_id"),
                   statuspage_repo_component_id = get_required_env("statuspage_repo_component_id"),
                   statuspage_website_component_id = get_required_env("statuspage_website_component_id"),
                   )

app.synth()

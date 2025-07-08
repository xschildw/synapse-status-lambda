#!/usr/bin/env python3
import os
import aws_cdk as cdk

from synapse_status.synapse_status_stack import SynapseStatusStack


def get_required_env(key: str) -> str:
  value = os.environ.get(key)
  if value is None or value == "":
    raise ValueError(f"Missing environment variable: {key}")
  return value

app = cdk.App()
SynapseStatusStack(app, "SynapseStatusStack",
  env = cdk.Environment(account=get_required_env("ACCOUNT_ID"), region="us-east-1"),
  statuspage_api_key = get_required_env("STATUSPAGE_API_KEY"),
  statuspage_page_id = get_required_env("STATUSPAGE_PAGE_ID"),
  statuspage_repo_component_id = get_required_env("STATUSPAGE_REPO_COMPONENT_ID"),
  statuspage_website_component_id = get_required_env("STATUSPAGE_WEBSITE_COMPONENT_ID"),
  vpc_id = get_required_env("VPC_ID")
  )

app.synth()

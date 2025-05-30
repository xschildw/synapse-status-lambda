#!/usr/bin/env python3
import aws_cdk as cdk

from synapse_status.synapse_status_stack import SynapseStatusStack


def check_context(key):
  value = app.node.try_get_context(key)
  if value is None:
    raise ValueError(f"Missing context variable: {key}")
  return value

app = cdk.App()
SynapseStatusStack(app, "SynapseStatusStack",
                   env = cdk.Environment(account=cdk.Aws.ACCOUNT_ID, region="us-east-1"),
                   statuspage_api_key = check_context("statuspage_api_key"),
                   statuspage_page_id = check_context("statuspage_page_id"),
                   statuspage_repo_component_id = check_context("statuspage_repo_component_id"),
                   statuspage_website_component_id = check_context("statuspage_website_component_id"),
                   )

app.synth()

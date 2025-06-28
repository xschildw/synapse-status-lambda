from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_ec2 as ec2,
)
from aws_cdk import aws_signer as signer
from constructs import Construct
from pathlib import Path

class SynapseStatusStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 statuspage_api_key: str,
                 statuspage_page_id: str,
                 statuspage_repo_component_id: str,
                 statuspage_website_component_id: str,
                 vpc_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a signing profile
        signing_profile = signer.SigningProfile(self, "SigningProfile", platform=signer.Platform.AWS_LAMBDA_SHA384_ECDSA )

        # Create a signing config using the profile
        signing_config = _lambda.CodeSigningConfig(self, "SigningConfig", signing_profiles=[signing_profile],
            untrusted_artifact_on_deployment=_lambda.UntrustedArtifactOnDeployment.ENFORCE
        )

        vpc = ec2.Vpc.from_lookup(self, "SynapseVPC", vpc_id=vpc_id)

        function = _lambda.Function(
            self, "StatusUpdaterFunction",
            runtime=_lambda.Runtime.NODEJS_22_X,
            handler="statuspage_updater.handler",
            code=_lambda.Code.from_asset(str(Path(__file__).parent.parent / "lambda")),
            environment={
                "REPO_STATUS_ENDPOINT": "https://repo-prod.prod.sagebase.org/repo/v1/status",
                "WEBSITE_URL_ENDPOINT": "https://www.synapse.org",
                "STATUS_PAGE_IO_API_KEY": statuspage_api_key,
                "STATUS_PAGE_IO_PAGE_ID": statuspage_page_id,
                "STATUS_PAGE_IO_REPO_COMPONENT_ID": statuspage_repo_component_id,
                "STATUS_PAGE_IO_WEBSITE_COMPONENT_ID": statuspage_website_component_id,
            },
            timeout=Duration.seconds(30),
            code_signing_config=signing_config,
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS, availability_zones=['us-east-1a', 'us-east-1c'])
        )

        # rule = events.Rule(
        #     self, "ScheduleRule",
        #     schedule=events.Schedule.rate(Duration.minutes(5)),
        # )
        # rule.add_target(targets.LambdaFunction(function))
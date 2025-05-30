from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
)
from constructs import Construct
from pathlib import Path

class SynapseStatusStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 statuspage_api_key: str,
                 statuspage_page_id: str,
                 statuspage_repo_component_id: str,
                 statuspage_website_component_id: str,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        function = _lambda.Function(
            self, "StatusUpdaterFunction",
            runtime=_lambda.Runtime.NODEJS_18_X,
            handler="status_updater.handler",
            code=_lambda.Code.from_asset(str(Path(__file__).parent.parent / "lambda")),
            environment={
                "REPO_STATUS_ENDPOINT": "https://repo-prod.prod.sagebase.org/repo/v1/status",
                "WEBSITE_URL_ENDPOINT": "https://www.synapse.org",
                "STATUS_PAGE_IO_API_KEY": statuspage_api_key,
                "STATUS_PAGE_IO_PAGE_ID": statuspage_page_id,
                "STATUS_PAGE_IO_REPO_COMPONENT_ID": statuspage_repo_component_id,
                "STATUS_PAGE_IO_WEBSITE_COMPONENT_ID": statuspage_website_component_id,
            },
        )

        rule = events.Rule(
            self, "ScheduleRule",
            schedule=events.Schedule.rate(Duration.minutes(5)),
        )
        rule.add_target(targets.LambdaFunction(function))

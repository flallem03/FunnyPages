import boto3
import sagemaker

from pipelines.funnytravis.pipeline import get_pipeline


region = boto3.Session().region_name
role = sagemaker.get_execution_role()
default_bucket = sagemaker.session.Session().default_bucket()

# Change these to reflect your project/business name or if you want to separate ModelPackageGroup/Pipeline from the rest of your team
pipeline_name = f"FunnyTravis"

pipeline = get_pipeline(
    region=region,
    role=role,
    default_bucket=default_bucket,
    pipeline_name=f"{pipeline_name}",
    base_job_prefix=pipeline_name
)

pipeline.upsert(role_arn=role)
print(pipeline)

client = boto3.client("sagemaker")

response = client.update_pipeline(
    PipelineName=f'{pipeline_name}-PROD',
    PipelineDisplayName=f'{pipeline_name}-PROD',
    PipelineDescription='test',
)
print(response)

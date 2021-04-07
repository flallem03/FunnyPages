import boto3
import sagemaker
import git
import sys

from pipelines.funnytravis.pipeline import get_pipeline



def deploy(name, version):
    # Change these to reflect your project/business name or if you want to separate ModelPackageGroup/Pipeline from the rest of your team
    pipeline_name = f"FunnyTravis-{name}"

    pipeline = get_pipeline(
        region=region,
        role=role,
        version=version,
        default_bucket=default_bucket,
        pipeline_name=f"{pipeline_name}",
        base_job_prefix=pipeline_name
    )
    return 0

    pipeline.upsert(role_arn=role)
    print(pipeline)

    client = boto3.client("sagemaker")

    response = client.update_pipeline(
        PipelineName=f'{pipeline_name}',
        PipelineDisplayName=f'{pipeline_name}-{version}',
        PipelineDescription='test',
    )
    print(response)



region = boto3.Session().region_name
role = sagemaker.get_execution_role()
default_bucket = sagemaker.session.Session().default_bucket()


supported_tags = list()
with open('SUPPORTED_TAGS') as tags: 
    supported_tags = tags.read().splitlines()

print (supported_tags)

# Get current tag set 
repo = git.Repo("./")
for tag in [ tag.name for tag in repo.tags if tag.commit == repo.head.commit ]:
    if tag in supported_tags:
        print(f"update pipeline for {str(tag)}")
        deploy(name=tag,version=str(repo.head.commit.hexsha[:7]))
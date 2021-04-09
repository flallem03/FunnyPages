import boto3
import sagemaker
import git
import sys
import logging

from pipelines.funnytravis.pipeline import get_pipeline

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)


region = boto3.Session().region_name

#Get Role
#Must set ROLE or ROLE_ARN as environment variables
try:
    role = sagemaker.get_execution_role()
except:
    logging.info("couldn\'t get role from sagemaker session")
    #ROLE must be set as an environment variable
    try:
        role = boto3.client('iam').get_role(RoleName=str(os.environ.get('ROLE')))['Role']['Arn']
    except:
        logging.info("couldn\'t get role from sagemaker session nor from ROLE")
        #ROLE_ARN must be set as an environment variable
        role = os.environ.get('ROLE_ARN')
        if role == None:
            raise Exception("Couldn't get Role for SageMaker")
            
default_bucket = sagemaker.session.Session().default_bucket()


supported_tags = list()
with open('SUPPORTED_TAGS') as tags: 
    supported_tags = tags.read().splitlines()
    
supported_branches = list()
with open('SUPPORTED_BRANCHES') as branches: 
    supported_branches = branches.read().splitlines()

logging.info (f"Supported Tags: {supported_tags}")


def deploy(name, version):
    # Change these to reflect your project/business name or if you want to separate ModelPackageGroup/Pipeline from the rest of your team
    pipeline_name = f"FunnyTravis-{name}"

    pipeline = get_pipeline(
        region=region,
        role=role,
        version=version[:7],
        default_bucket=default_bucket,
        pipeline_name=f"{pipeline_name}",
        base_job_prefix=pipeline_name
    )
    logging.info(f"Pipeline : {pipeline}")

    client = boto3.client("sagemaker")
    
    #Create Pipeline if not existant
    pipeline.upsert(role_arn=role)
    
    response=client.update_pipeline(
            PipelineName=f'{pipeline_name}',
            PipelineDisplayName=f'{pipeline_name}-{version[:7]}',
            PipelineDescription=f'pipeline and code in version {version}',
            PipelineDefinition=pipeline.definition(),
            )
        
    logging.info(f"update response : {response}")



# Get current tag set 
repo = git.Repo("./")
"""for tag in [ tag.name for tag in repo.tags if tag.commit == repo.head.commit ]:
    if tag in supported_tags:
        print(f"update pipeline for {str(tag)}")
        deploy(name=tag,version=str(repo.head.commit.hexsha))"""

for branche in [ branche.name for branche in repo.branches if branche.commit == repo.head.commit ]:
    if branche in supported_branches:
        print(f"update pipeline for {str(branche)}")
        deploy(name=branche,version=str(repo.head.commit.hexsha))
    else:
        print(f"{str(branche)} not supported")
import boto3
import sagemaker
import git
import logging
import argparse, configparser
import os

from pipelines.funnytravis.pipeline import get_pipeline

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)


def check_args():
    """
        check argurment when script is called directly
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        required=False,
        dest="env",
        metavar="S",
        type=str,
        default="local",
        help="environment used to identify the configuration file - must be one of the supported Tag",
    )
    default_project = os.getcwd().split("/")[-1]
    parser.add_argument(
        "--PipelineName",
        type=str,
        required=False,
        dest="pipeline_name",
        default=default_project,
    )
    args = parser.parse_args()
    return args


def read_conf(file):
    """"
        read Configuration file with environment settings
        These files are at the root level and start with env.
    """
    config = configparser.ConfigParser()
    config.read(file)
    return config


def deploy(name, version, region, default_bucket, role, commit):
    """
        Deploy a Sagemaker pipeline
    """
    # pipeline name does not support _ and .
    pipeline_version = version.replace(".", "-").replace("_", "-")
    pipeline_name = name.replace(".", "-").replace("_", "-")

    pipeline = get_pipeline(
        region=region,
        role=role,
        version=pipeline_version,
        default_bucket=default_bucket,
        pipeline_name=pipeline_name,
        base_job_prefix=pipeline_name,
    )

    logging.info(f"Pipeline : {pipeline_name}")

    client = boto3.client("sagemaker")
    if client.list_pipelines(PipelineNamePrefix=pipeline_name)["PipelineSummaries"]:
        # update an existing pipeline
        response = client.update_pipeline(
            PipelineName=f"{pipeline_name}",
            PipelineDisplayName=f"{pipeline_name}-{pipeline_version}",
            PipelineDescription=f"Pipeline for project{pipeline_name.split('-') [0]}    ;    "
            f"Environment : {pipeline_name.split('-')[1]}    ;     "
            f"code in version {version}    ;     "
            f"commit id : {commit}",
            PipelineDefinition=pipeline.definition(),
            RoleArn=role,
        )
        logging.info(f"update response : {response}")
    else:
        # pipeline does not exists
        response = client.create_pipeline(
            PipelineName=f"{pipeline_name}",
            PipelineDisplayName=f"{pipeline_name}-{version}",
            PipelineDescription=f"pipeline and code in version {version}",
            PipelineDefinition=pipeline.definition(),
            RoleArn=role,
        )


if __name__ == "__main__":
    # validate args
    args = check_args()
    logging.info(f"script arguments : {args}")

    # init context
    region = boto3.Session().region_name
    role = sagemaker.get_execution_role()
    default_bucket = sagemaker.session.Session().default_bucket()

    supported_tags = list()
    with open("SUPPORTED_TAGS") as tags:
        supported_tags = tags.read().splitlines()

    logging.info(f"Supported Tags: {supported_tags}")

    # Get current tag set
    repo = git.Repo("./")
    for tag in [tag.name for tag in repo.tags if tag.commit == repo.head.commit]:
        logging.info(f"extract tag : {tag}")
        splited_tag = tag.split("_")
        if len(splited_tag) > 2:
            project_name = splited_tag[0]
            environment = splited_tag[1]
            version = "_".join(splited_tag[2:])
            logging.info(
                f"Deployment of project {project_name} in environment {environment} for version {version}"
            )
            if environment in supported_tags:
                logging.info(f"update pipeline for {project_name}_{environment}")
                deploy(
                    name=f"{project_name}-{environment}",
                    version=version,
                    region=region,
                    default_bucket=default_bucket,
                    role=role,
                    commit=str(repo.head.commit),
                )
            else:
                logging.warning(
                    f"unsupported environment for tag : {tag}. Tag will be ignored"
                )
        else:
            logging.warning(f"unsupported tag format for: {tag}. Tag will be ignored")

#!make

PROJECT_NAME=FunnyPage
ENV=test
PipelineName=''
ifndef ENV
        $(error "ENV is undefined")
endif


help: ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\.PHONY: //' | sed -e 's/##//'


.PHONY: install-requirements
install-requirements: ## install local packages for local tests
	if [ ! -d "venv" ]; then \
		echo "venv is not installed"; \
		python3 -m venv venv ; \
	fi
	export PATH=./venv/bin/:${PATH}; source venv/bin/activate; pip install -r requirements.txt 


.PHONY: deploy-pipeline-only##: Deploy a Sagemaker pipeline for this project
deploy-pipeline-only: 
	@echo ================================================================================================================
	@echo ================================================================================================================
	@python3 deploy_pipeline.py


.PHONY: deploy-pipeline##: Deploy a Sagemaker pipeline for this project
deploy-pipeline: deploy-docker-image deploy-pipeline-only


.PHONY: deploy-docker-image##: Build and Deploy to AWS ECR Private registry a new papermill image
deploy-docker-image: 
	@echo ================================================================================================================
	@echo ================================================================================================================
	@echo ${ENV}
	#@python3 scripts/deploy_docker_image.py --env ${ENV}

.PHONY: test-container##:  Test a deployed container in a SageMaker Processing Job
test-container: 
	@echo ================================================================================================================
	@echo ================================================================================================================
	#@python3 scripts/test_deployed_container.py --env ${ENV}

.PHONY: execute-pipeline##:  Test a deployed SageMaker pipeline
execute-pipeline: 
	@echo ================================================================================================================
	@echo ================================================================================================================
	@python3 pipeline/execute_pipeline.py --env ${ENV} --PipelineName ${PipelineName}

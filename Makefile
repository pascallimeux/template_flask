.PHONY: default
default: help;

RED    := $(shell tput -Txterm setaf 1)
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

SHELL := /bin/bash
export PROJECTPATH:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

# Docker image for app
APP_VERSION=0.0.1
APP_IMAGE_NAME=app

# folders
BUILDFOLDER=${PROJECTPATH}/build
CERTFOLDER=${PROJECTPATH}/cert

# Python env
VENV=.venv
VENV_ACTIVATE= source ${VENV}/bin/activate
PYTHON= ${VENV}/bin/python3
PIP=${VENV}/bin/pip

# VM configuration
VMIP ?= 192.168.20.121
VMPORT ?= 5000
VMUSER = pascal


setup: ##@Dev Setup local dev environment.
	@if [ ! -d ${VENV} ]; then \
	    python3.8 -m venv ${VENV} || (echo "create ${VENV} failed $$?"; exit 1) && \
        ${PIP} install -r requirements.txt || (echo "install python modules failed $$?"; exit 1) && \
        echo "Python virtual environment installed."; \
	else \
        echo "Python venv already exists!"; \
    fi

run: ##@Dev Run main.py
	@export FLASK_DEBUG=1 && export FLASK_ENV=development && ${PYTHON} run.py
    
clear: ##@Dev Clear local dev environment.
	@rm -Rf ${VENV} 
	@rm -Rf __pycache__/
	@rm -Rf ${CERTFOLDER}
	@rm -Rf ${BUILDFOLDER}
	@find . -name app.tgz -delete 
	@find . -name '*.pyc' -delete
	@echo "Python virtual environment removed."

startdb: ##@DB Start mongoDB container.
	@docker-compose up -d mongo mongo-express

initdb: ##@DB Init admin account in DB.
	@docker-compose up -d mongo mongo-express
	@${VENV_ACTIVATE} && export FLASK_APP=run.py  && flask initdb admin
	@docker-compose stop

cleardb: ##@DB Stop and clear mongoDB container.
	@docker-compose down

docker: ##@Docker Build docker container (default VMIP=192.168.20.53 VMPORT=5000)
	$(call GenKeys)
	$(call CreateBuild)
	@cd ${BUILDFOLDER} && docker build -t ${APP_IMAGE_NAME}:${APP_VERSION} .
	@docker images |grep ${APP_IMAGE_NAME}


docker-run: ##@Docker Start server in docker container
	@docker-compose up -d

tgz: clear
	@echo build app.tgz
	@cd .. && tar czf app.tgz ./template_flask && mv app.tgz ${PROJECTPATH}/

rconfig: ##@Remote Display configuration for deploiement. 
	@$(call DisplayEnv)

deploy: docker ##@Remote Deploy application on VM (default VMIP=192.168.20.121 VMPORT=5000)
	@echo "${GREEN} > save locale docker image:  /tmp/${APP_IMAGE_NAME}:${APP_VERSION}.tgz ${RESET}"
	@docker save ${APP_IMAGE_NAME}:${APP_VERSION} > /tmp/${APP_IMAGE_NAME}:${APP_VERSION}.tgz
	@ssh-copy-id ${VMUSER}@${VMIP}
	@ssh $(VMUSER)@$(VMIP) 'mkdir /home/${VMUSER}/${APP_IMAGE_NAME}'
	@echo "${GREEN} > transfert files from local to ${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME} ${RESET}"
	@scp /tmp/${APP_IMAGE_NAME}:${APP_VERSION}.tgz ${VMUSER}@${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@scp ${PROJECTPATH}/docker-compose.yaml ${VMUSER}@${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@echo "${GREEN} > load image ${APP_IMAGE_NAME}:${APP_VERSION} on server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'docker load -i /home/${VMUSER}/${APP_IMAGE_NAME}/${APP_IMAGE_NAME}:${APP_VERSION}.tgz; rm /home/${VMUSER}/${APP_IMAGE_NAME}/${APP_IMAGE_NAME}:${APP_VERSION}.tgz'


rinitdb: ##@Remote Init database on remote VM
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down'
	@echo "${GREEN} > start docker containers on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose up -d'
	@echo "${GREEN} > init database on remote server ${VMIP} ${RESET}"	
	@ssh $(VMUSER)@$(VMIP) 'docker exec  myapp bash -c "export FLASK_APP=run.py  && flask initdb admin"'

rstop: ##@Remote Stop application on remote VM
	@echo "${GREEN} > stopping container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose stop' 

rstart: ##@Remote Start application on remote VM
	@echo "${GREEN} > starting container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose up -d'

rdown: ##@Remote Down application on remote VM
	@echo "${GREEN} > remove container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down'

rclean: ##@Remote Remove application on remote VM
	@echo "${GREEN} > remove application and container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down; docker rmi ${APP_IMAGE_NAME}:${APP_VERSION}; rm -rf /home/${VMUSER}/${APP_IMAGE_NAME}'

define Banner
    echo
    echo "      **********************************"
    echo "      *          FLASK TEMPLATE        * "
    echo "      **********************************"
    echo
endef

HELP_FUN = \
	%help; \
        while(<>) { push @{$$help{$$2 // 'options'}}, [$$1, $$3] if /^([a-zA-Z\-]+)\s*:.*\#\#(?:@([a-zA-Z\-]+))?\s(.*)$$/ }; \
        print "usage: make [target]\n\n"; \
        for (sort keys %help) { \
        print "${WHITE}$$_:${RESET}\n"; \
        for (@{$$help{$$_}}) { \
        $$sep = " " x (32 - length $$_->[0]); \
        print "  ${YELLOW}$$_->[0]${RESET}$$sep${GREEN}$$_->[1]${RESET}\n"; \
        }; \
        print "\n"; }

help: ##@other Show this help.
	@$(call Banner)
	@perl -e '$(HELP_FUN)' $(MAKEFILE_LIST)


define GenKeys
	@echo "${GREEN} > generate keys and certificates for server:${VMIP} ${RESET}"
	@if [ -d ${CERTFOLDER} ]; then rm -rf ${CERTFOLDER}; fi
	@mkdir ${CERTFOLDER}
	openssl req -x509 -newkey rsa:4096 -nodes -out ${CERTFOLDER}/server.crt -keyout ${CERTFOLDER}/server.key -days 365 -new -subj "/C=FR/ST=Paris/L=Paris/O=Orange/OU=R&D/CN=${VMIP}"
endef


define CreateBuild
	@echo "${GREEN} > Update code with server address=$(VMIP):$(VMPORT) ${RESET}"
	@if [ -d ${BUILDFOLDER} ]; then rm -rf ${BUILDFOLDER}; fi
	@mkdir ${BUILDFOLDER}
	@cp -R app ${BUILDFOLDER}
	@cp -R cert ${BUILDFOLDER}
	@cp Dockerfile ${BUILDFOLDER}
	@cp requirements.txt ${BUILDFOLDER}
	@cp run.py ${BUILDFOLDER}
	@sed -i -e 's/const url=.*/const url=\"https:\/\/$(VMIP):$(VMPORT)\"/g' ${BUILDFOLDER}/app/static/js/script.js
endef


define DisplayEnv
    echo "${WHITE}"
    echo "  IP VM -------------- ${VMIP}"
    echo "  USER ON VM --------- ${VMUSER}"
    echo "  SERVER PORT ON VM -- ${VMPORT}"
    echo "  APP VERSION -------- ${APP_VERSION}"
    echo "${RESET}"
endef


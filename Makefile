.PHONY: default
default: help;

RED    := $(shell tput -Txterm setaf 1)
GREEN  := $(shell tput -Txterm setaf 2)
WHITE  := $(shell tput -Txterm setaf 7)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

SHELL := /bin/bash
export PROJECTPATH:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
include .env

BUILDFOLDER=${PROJECTPATH}/build
KEYFILEPATH=${PROJECTPATH}/${KEYFILE}
CRTFILEPATH=${PROJECTPATH}/${CERTFILE}

ifndef LOCALIP
  OS := $(shell uname)
    ifeq ($(OS), Darwin)
    LOCALIP = $(shell ifconfig | grep -Eo 'inet (addr:)?([0-;9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | awk '{print $1}')
  endif

  ifeq ($(OS), Linux)
    LOCALIP = $(shell ip route get 8.8.8.8 | sed -n '/src/{s/.*src *\([^ ]*\).*/\1/p;q}')
  endif
endif

ifeq (${SECURE_MODE}, 1)
PROTOCOL := https
else
PROTOCOL := http
endif

# Python env
VENV=.venv
VENV_ACTIVATE= source ${VENV}/bin/activate
PYTHON= ${VENV}/bin/python3
PIP=${VENV}/bin/pip


startdb: ##@DB Start mongoDB container.
	@echo "${GREEN} > Start mongoDB and mongo-express docker containers ${RESET}"
	@docker-compose up -d mongo mongo-express
	@docker ps

cleardb: ##@DB Stop and clear mongoDB container.
	@echo "${GREEN} > Stop mongoDB and mongo-express docker containers ${RESET}"
	@docker-compose down

setup: ##@Dev Install Python virtual environment.
	@echo "${GREEN} > Create virtual environment for application ${RESET}"
	@if [ ! -d ${VENV} ]; then \
	    echo "Install Python virtual environment ..." && \
	    python3.8 -m venv ${VENV} > /dev/null 2>&1 || (echo "create ${VENV} failed $$?"; exit 1) && \
		${PIP} install wheel > /dev/null 2>&1  && \
        ${PIP} install -r requirements.txt > /dev/null 2>&1 || (echo "install python modules failed $$?"; exit 1) && \
        echo "Python venv installed."; \
	else \
        echo "Python venv already exists!"; \
    fi


init: ##@Dev Init admin account in DB, secretkey for flask and set IP address on javascript config file
	@echo "${GREEN} > Create admin account, secret key and update server IP address in JS config file ${RESET}"
	@if [ -n ${LOCALIP} ]; then echo Use local ip:${LOCALIP} to configure app; else echo "${RED}No IP connection ${RESET}"; exit 1; fi
	@docker-compose up -d mongo mongo-express > /dev/null 2>&1 || (echo "start db container failed $$?"; exit 1)
	@echo Init first admin in database
	@${VENV_ACTIVATE} && export FLASK_APP=run.py && flask initdb admin > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@echo Generate secret key for Flask server
	@${VENV_ACTIVATE} && export FLASK_APP=run.py && flask gensecretkey > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@echo Update server address in js configuration file
	@${VENV_ACTIVATE} && export SERVER_IP=${LOCALIP} && export FLASK_APP=run.py  && flask setipserver > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	$(call GenKeys,${LOCALIP}, ${CRTFILEPATH},${KEYFILEPATH})
	@docker-compose stop > /dev/null 2>&1 || (echo "stop db container failed $$?"; exit 1)


env: ##@Dev Display configuration. 
	@echo "${GREEN} > Display configuration ${RESET}"
	@$(call DisplayEnv)

run: ##@Dev Start Python application (needed DB)
	@echo "${GREEN} > Start Python application ${RESET}"
	@export SERVER_IP=${LOCALIP} && export FLASK_DEBUG=1 && export FLASK_ENV=development && ${PYTHON} run.py

clear: ##@Dev Clear local dev environment.
	@echo "${GREEN} > Remove environment ${RESET}"
	@rm -Rf __pycache__/
	@find . -name '*.pyc' -delete
	@if [ -d ${VENV} ]; then rm -rf ${VENV} && echo "Python virtual environment removed"; fi
	@if [ -d ${BUILDFOLDER} ]; then rm -rf ${BUILDFOLDER}/* && echo "Build folder removed"; else mkdir ${BUILDFOLDER}; fi	
	@if [ -f ${KEYFILEPATH} ]; then rm ${KEYFILEPATH} &&  echo Delete ${KEYFILEPATH}; fi
	@if [ -f ${CRTFILEPATH} ]; then rm ${CRTFILEPATH} &&  echo Delete ${CRTFILEPATH}; fi


docker: ##@Docker Build docker container
	$(call CreateBuild)
	$(call GenKeys,${LOCALIP},${BUILDFOLDER}/${CERTFILE},${BUILDFOLDER}/${KEYFILE})
	@echo build Docker image ${APP_IMAGE_NAME}:${APP_VERSION} ...
	@cd ${BUILDFOLDER} && docker build -t ${APP_IMAGE_NAME}:${APP_VERSION} . > /dev/null 2>&1 || (echo "build image failed $$?"; exit 1)
	@docker images ${APP_IMAGE_NAME}:${APP_VERSION}


docker-run: ##@Docker Start server in docker container
	@echo "${GREEN} > Start application in docker containers ${RESET}"
	@export SERVER_IP=${LOCALIP} && docker-compose up -d

docker-stop: ##@Docker Stop server in docker container
	@echo "${GREEN} > Stop application in docker containers ${RESET}"
	@export SERVER_IP=${LOCALIP} && docker-compose stop

docker-down: ##@Docker Remove app containers
	@echo "${GREEN} > Remove docker containers of application ${RESET}"
	@export SERVER_IP=${LOCALIP} && docker-compose down


tgz: clear
	@echo "${GREEN} > Build tgz archive of source code in build folder ${RESET}"
	@echo build  ${BUILDFOLDER}/app.tgz
	@cd .. && tar czf app.tgz ./template_flask && mv app.tgz ${BUILDFOLDER}/app.tgz


deploy: ##@Remote Deploy application on VM
	@echo "${GREEN} > deploy application on server ${VMIP} ${RESET}"
	$(call CreateBuild)
	$(call GenKeys,${VMIP},${BUILDFOLDER}/${CERTFILE},${BUILDFOLDER}/${KEYFILE})
	@echo Generate secret key
	@${VENV_ACTIVATE} && cd ${BUILDFOLDER} && export FLASK_APP=run.py  && flask gensecretkey > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@echo Update server IP address
	@sed -i -e 's/const url =.*/const url=\"https:\/\/$(VMIP):$(VMPORT)\"/g' ${BUILDFOLDER}/app/static/js/settings.js > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@echo create docker image of application...
	@cd ${BUILDFOLDER} && docker build -t ${APP_IMAGE_NAME}:${APP_VERSION} . > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@echo save locale docker image:  ${BUILDFOLDER}/${APP_IMAGE_NAME}:${APP_VERSION}.tgz
	docker save ${APP_IMAGE_NAME}:${APP_VERSION} > ${BUILDFOLDER}/${APP_IMAGE_NAME}.tgz
	@echo copy ssh id on remote server
	@ssh-copy-id ${VMUSER}@${VMIP} > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down; docker rmi ${APP_IMAGE_NAME}:${APP_VERSION} > /dev/null 2>&1; rm -rf /home/${VMUSER}/${APP_IMAGE_NAME} > /dev/null 2>&1'
	@ssh $(VMUSER)@$(VMIP) 'mkdir /home/${VMUSER}/${APP_IMAGE_NAME}'
	@echo transfert files from local to ${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@scp ${BUILDFOLDER}/${APP_IMAGE_NAME}.tgz ${VMUSER}@${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@scp ${PROJECTPATH}/docker-compose.yaml ${VMUSER}@${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@echo -e "SERVER_PORT=${VMPORT}\nCERTFILE=${CERTFILE}\nKEYFILE=${KEYFILE}\n" > ${BUILDFOLDER}/.env
	@scp ${BUILDFOLDER}/.env ${VMUSER}@${VMIP}:/home/${VMUSER}/${APP_IMAGE_NAME}
	@echo load image ${APP_IMAGE_NAME}:${APP_VERSION} on server ${VMIP}
	@ssh $(VMUSER)@$(VMIP) 'docker load -i /home/${VMUSER}/${APP_IMAGE_NAME}/${APP_IMAGE_NAME}.tgz'


rinitdb: ##@Remote Init database on remote VM
	@echo "${GREEN} > start docker containers on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose up -d'
	@echo "${GREEN} > init first admin account in DB on remote server ${VMIP} ${RESET}"	
	@ssh $(VMUSER)@$(VMIP) 'docker exec  myapp bash -c "export FLASK_APP=run.py  && flask initdb admin"'

rstop: ##@Remote Stop application on remote VM
	@echo "${GREEN} > stop container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose stop' 

rstart: ##@Remote Start application on remote VM
	@echo "${GREEN} > starting container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose up -d'

rdown: ##@Remote Delete containers on remote VM
	@echo "${GREEN} > remove container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down'

rclean: ##@Remote Remove application on remote VM
	@echo "${GREEN} > remove application and container on remote server ${VMIP} ${RESET}"
	@ssh $(VMUSER)@$(VMIP) 'cd /home/${VMUSER}/${APP_IMAGE_NAME} && docker-compose down ; docker rmi ${APP_IMAGE_NAME}:${APP_VERSION} > /dev/null 2>&1; rm -rf /home/${VMUSER}/${APP_IMAGE_NAME} > /dev/null 2>&1' > /dev/null >&1 || (echo "command failed $$?"; exit 1)

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

# params IP CRTFILEPATH KEYFILEPATH
define GenKeys
	@echo Generate keys and certificates for server:$1
	@openssl req -x509 -newkey rsa:4096 -nodes -out $2 -keyout $3 -days 365 -new -subj "/C=FR/ST=Paris/L=Paris/O=Orange/OU=R&D/CN=$1" > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
    @echo certificate information:
	@openssl x509 -noout -in server.crt -issuer -dates
endef


define CreateBuild
	@if [ -d ${BUILDFOLDER} ]; then rm -rf ${BUILDFOLDER}/*; else mkdir ${BUILDFOLDER}; fi
	@cp -R app ${BUILDFOLDER} > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@cp Dockerfile ${BUILDFOLDER} > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@cp requirements.txt ${BUILDFOLDER} > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
	@cp run.py ${BUILDFOLDER} > /dev/null 2>&1 || (echo "command failed $$?"; exit 1)
endef


define DisplayEnv
    echo "${WHITE}"
    echo "  VM URL -------------- https://${VMIP}:${VMPORT}"
    echo "  VM USER ------------- ${VMUSER}"
	echo
	echo "  LOCAL URL ----------- ${PROTOCOL}://${LOCALIP}:${SERVER_PORT}"
	echo "  LOCAL OS ------------ ${OS}"
	echo "  LOG LEVEL ----------- ${LOG_LEVEL}"
    echo "  DOCKER IMAGE -------- ${APP_IMAGE_NAME}:${APP_VERSION}"
    echo "${RESET}"
endef


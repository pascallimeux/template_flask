# template

## update .env to define environment variables


## generate certificate in cert folder

```
openssl req -x509 -newkey rsa:4096 -nodes -out server.crt -keyout server.key -days 365 -new -subj "/C=IL/ST=Tel Aviv/L=Tel Aviv/O=ONU/OU=Def/CN=samaritan"
openssl req -x509 -newkey rsa:4096 -nodes -out server.crt -keyout server.key -days 1000 -new -subj "/C=FR/ST=PAris/L=Paris/O=Orange/OU=R&D Department/CN=production"
```

## read certificate in cert folder

```
openssl x509 -in server.crt -text
```

## build tgz archive of source
Clear environment and build a tgz file for source code
```
make tgz
```

## Project setup
Generate python virtual environment
```
make setup
```

## Project init
Init admin account in DB, secretkey for flask and set IP address on javascript config file
```
make init
```

### Clear project
Remove build folder, virtual env and keys certificates
```
make clear
```

### Start DB
Start mongo and mongo-express docker containers
```
make startdb
```

### Init DB
Init admin account in DB, secretkey for flask and set IP address on javascript config file
```
make initdb
```

### Clear DB
remove mongo container
```
make cleardb
```

### Start application
start python code
```
make run
```
### URLs

[application](http://localhost:5000)  
[mongo express](http://localhost:8081)

### Generate application Docker image 
Buid a docker container for app
```
make docker
```

### Start local docker application with mongo and mongo-express
Start mongo mongo-express and app docker containers
```
make docker-run
```

### Deploy application on remote VM

```
make deploy
```


### Process to install from github (requirements: make docker docker-compose)

```
git clone https://github.com/pascallimeux/template_flask.git
cd template_flask
make setup init startdb run to run python app

make setup init docker docker-run to run docker app

make setup deploy rinitdb rstart to run docker app in remote VM
```
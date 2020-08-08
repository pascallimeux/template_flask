# template

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

```
make tgz
```

## Project setup

```
make setup
```

### Clear project

```
make clear
```

### Start DB

```
make startdb
```

### Init DB

```
make initdb
```

### Clear DB

```
make cleardb
```

### Start application

```
make run
```
### URLs

[application](http://localhost:5000)  
[mongo express](http://localhost:8081)

### Generate application Docker image 

```
make docker
```

### Start local docker application with mongo and mongo-express

```
make docker-run
```

### Deploy application on remote VM

```
make deploy VMIP=X.X.X.X VMPORT=XXXX VMUSER=toto
```


### Process to install from github (requirements: make docker docker-compose)

```
git clone https://github.com/pascallimeux/template_flask.git
cd template_flask
make setup initdb startdb run
```
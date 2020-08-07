# template

## generate certificate in cert folder

```
openssl req -x509 -newkey rsa:4096 -nodes -out server.crt -keyout server.key -days 365 -new -subj "/C=IL/ST=Tel Aviv/L=Tel Aviv/O=ONU/OU=Def/CN=samaritan"
```

## read certificate in cert folder

```
openssl x509 -in server.crt -text
```

## build source code tgz

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


### Process to install from github

```
git clone 
make setup
```
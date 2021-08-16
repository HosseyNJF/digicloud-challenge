# DigiCloud Challenge Project

## About

This is the repository hosting the code for **the entry challenge of DigiCloud**.

## Requirements
- Docker (version 19.03.0 or later)
- Docker compose

## Deploy
- Clone the repo:
`git clone git@github.com:HosseyNJF/digicloud-challenge.git`
- Copy `.env.example` to `.env`
- Copy `.env.local.example` to `.env.local`
- Add a new secret key to the local env file
- Run these commands:
```shell
docker-compose up -d
docker-compose exec app python manage.py migrate
```
- Open the application in the following address:
http://localhost:8090/api
- You can see the documentation there.

The register endpoint is accessible at: http://localhost:8090/api/register

The login endpoint is accessible at: http://localhost:8090/api/token

Alternatively, while using the browsable API you can login via session from here: http://localhost:8090/admin
# Testing
- Run the tests using this command:
```shell
docker-compose exec app python manage.py test
```

- Collect coverage data using this command:
```shell
docker-compose exec app python -m coverage run --source='.' manage.py test
```

- Observe the coverage data using this command:
```shell
docker-compose exec app python -m coverage report
```

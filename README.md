# ECO zone

## Requirements

- Python 3.12.3

## Development

### Set up development environment

```
git pull git@gitlab.com:qantic/eco_zone.git
cd eco_zone
python<3.12.3> -m venv .venv --prompt=eco_zone
. ./.venv/bin/activate
python -m pip install -r ./requirements/dev.txt -r ./requirements/main.txt
pre-commit init
python manage.py migrate
```

### Harvest redispatch data

```
export NETZTRANZPARENZ_CLIENT_ID=<your client id>
export NETZTRANZPARENZ_CLIENT_SECRET=<your client secret>
python manage.py harvest redispatch
```

### Start development server

```
python manage.py runserver
```

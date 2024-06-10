# ECO zone

# Requirements

- Python 3.12.3

# Development

## Set up development environment

```bash
git pull git@gitlab.com:qantic/ecozone.git
cd eco_zone
python<3.12.3> -m venv .venv --prompt=ecozone
. ./.venv/bin/activate
python -m pip install -r ./requirements/dev.txt -r ./requirements/main.txt
pre-commit init
python manage.py migrate
```

## Harvest redispatch data

```bash
export NETZTRANZPARENZ_CLIENT_ID=<your client id>
export NETZTRANZPARENZ_CLIENT_SECRET=<your client secret>
python manage.py harvest redispatch
```

## Start development server

```bash
python manage.py runserver
```

# Deployment

## Set up server

- Create a server on Hetzner (recommended: shared CPX31 with 4 VCPU, 8 GB RAM, 160 GB storage)
  - Enable backup for server via Hetzner panel
  - Include your public SSH key
- SSH into the server and install Dokku and plugins for Postgres and LetsEncrypt (use `sudo` if you are not root):
  - (See https://dokku.com/ for Dokku documentation)
    ```bash
    wget -NP . https://dokku.com/bootstrap.sh
    DOKKU_TAG=v0.34.4 bash bootstrap.sh
    dokku plugin:install https://github.com/dokku/dokku-postgres.git
    dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
    ```
  - If the server already has a domain:
    ```bash
    dokku domains:set-global <DOMAIN NAME>
    ```
    - If you don't set a domain, Dokku will just use the IP address
    - You can configure a domain later
    - Id a domain is set, apps will be deployed to a subdomain by default (e.g., `ecozone-dev.domainname.com`)
    - If no domain is set, apps will be deployed to a port by default (e.g., `<IP-ADDRESS:1234>`)
  - Add your public key to Dokku (to deploy you'll need to `git push` as the `dokku` user, not at as `root`)
    ```bash
    PUBLIC_KEY="your-public-key-contents-here"
    echo "$PUBLIC_KEY" | dokku ssh-keys:add <UNIQUE NAME FOR KEY>
    ```
    - If you want other users to be able to deploy, repeat the process for their keys
  - Create the Dokku app
    ```bash
    dokku apps:create ecozone
    ```
  - Create a database for the app
    ```bash
    dokku postgres:create ecozone-db
    ```
  - Link the db to the app
    ```bash
    dokku postgres:link ecozone-db ecozone
    ```
- On your machine:
  - Add a Git remote to the repository
    ```bash
    git remote add <NAME OF REMOTE> dokku@<IP ADDRESS OR DOMAIN>:ecozone
    ```
   - If you will be deploying to more than one server, create a different remote for each (e.g., one remote named `ecozone-dev`, one named `ecozone-staging`, etc.). Note that the user will always be `dokku` (the `dokku@` part will remain the same for each remote)
- To deploy a new version, `git push` a local branch to the desired Dokku remote. You will always be pushing to the `main` branch on the Dokku remote.
  - Examples (assuming you are deploying to the `ecozone-dev` remote):
    - Deploy your `main` branch (i.e., deploy you `main` to the remote's `main`)
      ```bash
      git push --force ecozone-dev main
      ```
    - Deploy your `dev` branch (regardless of whether you have currently checked out the `dev` branch)
      ```bash
      git push --force ecozone-dev dev:main
      ```
    - Deploy whatever branch is currently checked out
      ```bash
      git push --force ecozone-dev $(git branch --show-current):main
      ```
  - Note: Using the `--force` flag is not strictly necessary in all cases but you'll probably need it. For example, if you deploy your `dev` branch, commit some changes to it locally, and then want to deploy them, you don't need to use `--force` because there will be no conflicts when you push. However, if you need to deploy different versions for testing or demonstration purposes and those branches do have conflicts, you'll need to use `--force` to ensure that the new version overwrites the old, conflicting version so that the deployment can continue.

## Set environment variables

In order to harvest redispatch data, `NETZTRANZPARENZ_CLIENT_ID` and `NETZTRANZPARENZ_CLIENT_SECRET` environment variables must be set. (See ["Harvest redispatch data"](#harvest-redispatch-data) for more about the harvesting process.)

To ensure that the environment variables are set every time Dokku deploys the app (or runs it for a cron job, etc.), use the following Dokku commands. You only have to run them once; Dokku will remember them for all future deployments.

```bash
dokku config:set ecozone NETZTRANZPARENZ_CLIENT_SECRET=<THE SECRET>
dokku config:set ecozone NETZTRANZPARENZ_CLIENT_ID=<THE ID>
```

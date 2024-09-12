# ECO zone

Das Projekt „ECO zone – Energiesteuerung und Emissionsreduktion durch zonale Analysen“ strebt die Entwicklung eines marginalen zonalen CO2-Emissionsmodells für das deutsche Stromnetz an. Durch die genaue Erfassung und Analyse lokaler Emissionsdaten soll eine zeitliche bzw. räumliche Verschiebung von Lasten ermöglicht werden, um die Abregelung erneuerbarer Erzeugungseinheiten im Redispatch zu minimieren.

Dieses Repository enthält den Quellcode für die begleitende Webanwendung. Die Webanwendung soll deutschlandweit eine intelligentere und umweltfreundlichere Energieverteilung ermöglichen. Weitere Informationen finden Sie hier: https://future-energy-lab.de/projects/eco-zone/.

# Inhalt
- [ECO zone](#eco-zone)
- [Inhalt](#inhalt)
- [Anforderungen](#anforderungen)
- [Entwicklung](#entwicklung)
  - [Entwicklungsumgebung einrichten](#entwicklungsumgebung-einrichten)
- [Daten abrufen](#daten-abrufen)
  - [Redispatch-Daten sammeln](#redispatch-daten-sammeln)
  - [Erzeugungsdaten sammeln](#erzeugungsdaten-sammeln)
  - [Zonen aktualisieren](#zonen-aktualisieren)
  - [Entwicklungsserver starten](#entwicklungsserver-starten)
- [Bereitstellung](#bereitstellung)
  - [Server einrichten](#server-einrichten)
  - [Umgebungsvariablen](#umgebungsvariablen)


# Anforderungen

- Python 3.12.3

# Entwicklung

## Entwicklungsumgebung einrichten

Diese Anweisungen setzen voraus, dass Sie Python 3.12.3 installiert und konfiguriert haben. Wenn Sie mehr als eine Version von Python auf Ihrem Computer haben, ersetzen Sie beim Erstellen der virtuellen Umgebung `python` durch die richtige Version, z. B. `python3.12`.

Nachdem Sie die folgenden Schritte abgeschlossen haben, haben Sie 1) eine virtuelle Umgebung erstellt, 2) alle Entwicklungsanforderungen installiert, 3) die Pre-Commit-Hooks installiert, die eine konsistente Codequalität für das Projekt gewährleisten, und 4) eine SQLite-Datenbank für die lokale Entwicklungsarbeit erstellt.

```bash
git pull git@github.com:ECO-zone/eco-zone.git
cd eco-zone
python -m venv .venv --prompt=eco-zone
. ./.venv/bin/activate
python -m pip install -r ./requirements/dev.txt -r ./requirements/main.txt
pre-commit init
python manage.py migrate
```

# Daten abrufen

Die Anwendung basiert auf Daten, die von netztranzparenz.de und ENTSO-E gesammelt wurden. Die Daten sind nicht in diesem Repo enthalten. Netztranzparenz.de und ENTSO-E aktualisieren die Daten regelmäßig und in der Produktion holen Harvester mehrmals täglich neue Daten ab. Um sicherzustellen, dass Sie mit korrekten und aktuellen Daten arbeiten, müssen Sie auch von netztranzparenz.de und ENTSO-E Daten sammeln.

Beachten Sie, dass sowohl Redispatch-Daten als auch Erzeugungsdaten erforderlich sind, um die Emissionsintensität zu berechnen.

## Redispatch-Daten sammeln

Um Redispatch-Daten von netztranzparenz.de zu sammeln, benötigen Sie eine Client-ID und ein Client-Geheimnis. Sie müssen sich unter https://extranet.netztransparenz.de/APIRegistrierung registrieren.

Verwenden Sie die folgenden Befehle, um Redispatch-Daten zu sammeln.

```bash
export NETZTRANZPARENZ_CLIENT_ID=<your client id>
export NETZTRANZPARENZ_CLIENT_SECRET=<your client secret>
python manage.py harvest redispatch
```

## Erzeugungsdaten sammeln

Um Erzeugungsdaten von ENTSO-E zu sammeln, benötigen Sie ein Sicherheitstoken. Sie müssen sich unter https://transparency.entsoe.eu/ registrieren (klicken Sie oben rechts auf den Link „Anmelden“ und dann unten im Anmeldeformular auf „Registrieren“).

Verwenden Sie die folgenden Befehle, um Erzeugungsdaten zu sammeln.

```bash
export ENTSOE_SECURITY_TOKEN=<your ENTSOE token>
python manage.py harvest psr
```

## Zonen aktualisieren

Die Anlagen, die in den Redispatch-Daten erscheinen, müssen Zonen zugewiesen werden. Die Zonenzuweisungen sind im Repository enthalten, müssen aber manuell zur Datenbank hinzugefügt werden.

Verwenden Sie den folgenden Befehl, um die Zonenzuweisungen in der Datenbank zu aktualisieren.

```bash
python manage.py update zones
```

## Entwicklungsserver starten

Nachdem Sie die Redispatch- und Generierungsdaten erfasst und die Zonen aktualisiert haben, können Sie den Entwicklungsserver starten, um mit der Anwendung zu interagieren. Beachten Sie, dass Sie die Daten nicht bei jedem Start des Entwicklungsservers erneut erfassen müssen. Sie müssen sie nur erneut erfassen, wenn Sie die neuesten Daten zu Ihrer Datenbank hinzufügen möchten.

Verwenden Sie den folgenden Befehl, um den Entwicklungsserver zu starten. Wenn dies erfolgreich ist, können Sie über Ihren Webbrowser unter http://localhost:8000/ auf die Anwendung zugreifen.

```bash
python manage.py runserver
```

# Bereitstellung

Die Anwendung kann auf jedem Linux-Server bereitgestellt werden, auf dem Python 3.12.3 (für eine Bare-Metal-Installation) oder Docker (oder ein System, das auf Docker basiert) läuft. Wie Sie die Anwendung bereitstellen, hängt von Ihren Anforderungen und den verfügbaren Ressourcen ab. Die folgenden Abschnitte beschreiben eine leichte, aber robuste Bereitstellung mit Dokku, die Sie schnell replizieren können sollten.

## Server einrichten

- Einen Server erstellen (empfohlen: ein gemeinsam genutzter Hetzner CPX31 mit 4 VCPU, 8 GB RAM, 160 GB Speicher)
  - Backups für den Server über das Control Panel aktivieren
  - Ihren öffentlichen SSH-Schlüssel hochladen
- Per SSH auf den Server zugreifen und Dokku und Plugins für Postgres und LetsEncrypt installieren (verwenden Sie `sudo`, wenn Sie nicht root sind):
  - (Die Dokku-Dokumentation finden Sie unter https://dokku.com/)
    ```bash
    wget -NP . https://dokku.com/bootstrap.sh
    DOKKU_TAG=v0.34.4 bash bootstrap.sh
    dokku plugin:install https://github.com/dokku/dokku-postgres.git
    dokku plugin:install https://github.com/dokku/dokku-letsencrypt.git
    ```
  - Wenn der Server bereits eine Domäne hat:
    ```bash
    dokku domains:set-global <DOMAINNAME>
    ```
    - Wenn Sie keine Domäne festlegen, verwendet Dokku einfach die IP-Adresse
    - Sie können später eine Domäne konfigurieren
    - Wenn eine Domäne festgelegt ist, werden Apps standardmäßig in einer Subdomäne bereitgestellt (z. B. `ecozone-dev.domainname.com`)
    - Wenn keine Domäne festgelegt ist, werden Apps standardmäßig in einem Port bereitgestellt (z. B. `<IP-ADRESSE:1234>`)
  - Fügen Sie Ihren öffentlichen Schlüssel zu Dokku hinzu (zum Bereitstellen müssen Sie `git push` als `dokku`-Benutzer ausführen, nicht als `root`)
    ```bash
    PUBLIC_KEY="Ihr-öffentlicher-Schlüssel-Inhalt-hier"
    echo "$PUBLIC_KEY" | dokku ssh-keys:add <EINDEUTIGER NAME FÜR SCHLÜSSEL>
    ```
    - Wenn Sie möchten, dass andere Benutzer bereitstellen können, wiederholen Sie den Vorgang für ihre Schlüssel
  - Erstellen Sie die Dokku-App
    ```bash
    dokku apps:create ecozone
    ```
  - Erstellen Sie eine Datenbank für die App
    ```bash
    dokku postgres:create ecozone-db
    ```
  - Verknüpfen Sie die Datenbank mit der App
    ```bash
    dokku postgres:link ecozone-db ecozone
    ```
  - Um sicherzustellen, dass die Umgebungsvariablen jedes Mal festgelegt werden, wenn Dokku die App bereitstellt (oder sie für einen Cron-Job usw. ausführt), verwenden Sie die folgenden Dokku-Befehle. Sie müssen sie nur einmal ausführen; Dokku merkt sie sich für alle zukünftigen Bereitstellungen. Weitere Informationen zu den einzelnen Umgebungsvariablen finden Sie unter ["Umgebungsvariablen"](#environment-variables).
    ```bash
    dokku config:set --no-restart ecozone NETZTRANZPARENZ_CLIENT_SECRET=<DAS GEHEIMNIS>
    dokku config:set --no-restart ecozone NETZTRANZPARENZ_CLIENT_ID=<DIE ID>
    dokku config:set --no-restart ecozone ENTSOE_SECURITY_TOKEN=<DAS TOKEN>
    dokku config:set --no-restart ecozone SENTRY_CDN_URL=<URL>
    dokku config:set --no-restart ecozone SENTRY_DSN_BACKEND=<URL>
    dokku config:set --no-restart ecozone SENTRY_ENVIRONMENT=<NAME DER UMGEBUNG> # Z. B. „dev“
    dokku config:set --no-restart ecozone SENTRY_RELEASE_URL_BACKEND=<URL>
    dokku config:set --no-restart ecozone SENTRY_RELEASE_URL_FRONTEND=<URL>
    ```
- Auf Ihrem Computer:
  - Fügen Sie dem Repository ein Git-Remote hinzu
    ```bash
    git remote add <NAME DES REMOTE> dokku@<IP-ADRESSE ODER DOMÄNE>:ecozone
    ```
    - Wenn Sie auf mehr als einem Server bereitstellen, erstellen Sie für jeden ein anderes Remote (z. B. ein Remote mit dem Namen `ecozone-dev`, ein Remote mit dem Namen `ecozone-staging` usw.). Beachten Sie, dass der Benutzer immer `dokku` sein wird (der Teil `dokku@` bleibt für jedes Remote gleich)
- Um eine neue Version bereitzustellen, `git push` Sie einen lokalen Branch zum gewünschten Dokku-Remote. Sie pushen immer zum `main`-Branch auf dem Dokku-Remote.
  - Beispiele (vorausgesetzt, Sie stellen auf dem Remote-Server `ecozone-dev` bereit):
    - Stellen Sie Ihren `main`-Branch bereit (d. h. stellen Sie Ihren `main` auf dem `main` des Remote-Servers bereit)
      ``bash
      git push --force ecozone-dev main
      ```
    - Stellen Sie Ihren `dev`-Branch bereit (unabhängig davon, ob Sie den `dev`-Branch aktuell ausgecheckt haben)
      ```bash
      git push --force ecozone-dev dev:main
      ```
    - Stellen Sie den aktuell ausgecheckten Branch bereit
      ```bash
      git push --force ecozone-dev $(git branch --show-current):main
      ```
  - Hinweis: Die Verwendung des Flags `--force` ist nicht in allen Fällen unbedingt erforderlich, aber Sie werden es wahrscheinlich brauchen. Wenn Sie beispielsweise Ihren `dev`-Branch bereitstellen, einige Änderungen lokal daran committen und sie dann bereitstellen möchten, müssen Sie `--force` nicht verwenden, da beim Pushen keine Konflikte auftreten. Wenn Sie jedoch zu Test- oder Demonstrationszwecken unterschiedliche Versionen bereitstellen müssen und diese Branches Konflikte aufweisen, müssen Sie „--force“ verwenden, um sicherzustellen, dass die neue Version die alte, konfliktbehaftete Version überschreibt, damit die Bereitstellung fortgesetzt werden kann.

## Umgebungsvariablen

Um Redispatch-Daten zu sammeln, müssen die Umgebungsvariablen `NETZTRANZPARENZ_CLIENT_ID` und `NETZTRANZPARENZ_CLIENT_SECRET` festgelegt werden. (Weitere Informationen zum Sammelvorgang finden Sie unter ["Redispatch-Daten sammeln"](#redispatch-daten-sammeln).)

Um Generationsdaten zu sammeln, muss die Umgebungsvariable `ENTSOE_SECURITY_TOKEN` festgelegt werden. (Weitere Informationen zum Sammelvorgang finden Sie unter ["Erzeugungsdaten sammeln"](#erzeugungsdaten-sammeln).)

Um Fehler im Frontend und Backend zu überwachen, ist die Anwendung so konfiguriert, dass sie [Sentry](https://sentry.io) verwendet. Die folgenden Umgebungsvariablen sind erforderlich, wenn die Anwendung auf einem Staging- oder Produktionsserver ausgeführt wird, werden jedoch weder benötigt noch verwendet, wenn ein lokaler Entwicklungsserver ausgeführt wird. Wir empfehlen, ein Django-Projekt auf Sentry für das Backend und ein Vanilla-JavaScript-Projekt auf Sentry für das Frontend zu erstellen.

- `SENTRY_CDN_URL` ist die URL zum Herunterladen von Sentry für das Frontend. Sie ist mit dem DSN für das Frontend vorkonfiguriert.

- `SENTRY_DSN_BACKEND` ist die DSN-URL für das Backend.

- `SENTRY_ENVIRONMENT` ist der Name der Umgebung, in der die Anwendung bereitgestellt wird, z. B. „dev“ oder „staging“.

- `SENTRY_RELEASE_URL_BACKEND` ist die Webhook-URL zum Registrieren einer Version für das Backend-Projekt.

- `SENTRY_RELEASE_URL_FRONTEND` ist die Webhook-URL zum Registrieren einer Version für das Frontend-Projekt.

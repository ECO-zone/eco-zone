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
  - [Erzeugungsdaten sammeln](#erzeugungsdaten-sammeln-1)
  - [Zonen aktualisieren](#zonen-aktualisieren)
  - [Entwicklungsserver starten](#entwicklungsserver-starten)
- [Bereitstellung](#bereitstellung)
  - [Server einrichten](#server-einrichten)
  - [Umgebungsvariablen](#umgebungsvariablen)
- [Datenquellen und -bearbeitung](#datenquellen-und--bearbeitung)
  - [Erzeugungsdaten](#erzeugungsdaten)
    - [Aktuelle und historische Erzeugungsdaten](#aktuelle-und-historische-erzeugungsdaten)
      - [Häufigkeit der Datenaktualisierung](#häufigkeit-der-datenaktualisierung)
  - [Erzeugungsprognosen](#erzeugungsprognosen)
    - [Zeitrahmen der Prognosen](#zeitrahmen-der-prognosen)
  - [Emissionsfaktoren](#emissionsfaktoren)
  - [Emissionen](#emissionen)
  - [Redispatch](#redispatch)
  - [Deutscher nationaler Emissionsfaktor](#deutscher-nationaler-emissionsfaktor)
  - [Zonale Emissionsfaktoren](#zonale-emissionsfaktoren)
    - [Beispiel: Der zonale Emissionsfaktor im Norden beträgt 0 kgCO2/MWh](#beispiel-der-zonale-emissionsfaktor-im-norden-beträgt-0-kgco2mwh)
    - [Beispiel: Der zonale Emissionsfaktor im Süden ist größer als der nationale Emissionsfaktor](#beispiel-der-zonale-emissionsfaktor-im-süden-ist-größer-als-der-nationale-emissionsfaktor)

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

## Erzeugungsdaten sammeln

Um Erzeugungsprognosen von ENTSO-E zu sammeln, benötigen Sie ein Sicherheitstoken. Sie müssen sich unter https://transparency.entsoe.eu/ registrieren (klicken Sie oben rechts auf den Link „Anmelden“ und dann unten im Anmeldeformular auf „Registrieren“).

Verwenden Sie die folgenden Befehle, um Erzeugungsprognosen zu sammeln.

```bash
export ENTSOE_SECURITY_TOKEN=<your ENTSOE token>
python manage.py harvest aggregate_forecast
python manage.py harvest renewable_forecast --forecast_type=day-ahead
python manage.py harvest renewable_forecast --forecast_type=intraday
python manage.py harvest renewable_forecast --forecast_type=current
python manage.py update forecasts
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
    dokku config:set --no-restart ecozone SECRET_KEY=<GEHEIMSCHLÜSSEL>
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

- `SECRET_KEY` ist der Geheimschlüssel für Django-Sessions.

# Datenquellen und -bearbeitung

## Erzeugungsdaten

### Aktuelle und historische Erzeugungsdaten

Die Erzeugungsdaten werden vom ENTSO-E-Transparenzportal (URL: https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType/show) bezogen. Die Auflösung der Daten beträgt 15 Minuten, sodass die mit jedem `start`-Zeitstempel verknüpften Erzeugungswerte die Erzeugung für den 15-Minuten-Zeitraum darstellen, der zu diesem Zeitpunkt beginnt. Die Maßeinheit ist MW. Daten sind für jede Energiequelle verfügbar.

#### Häufigkeit der Datenaktualisierung

Tagsüber werden alle 15 Minuten die Daten der letzten sieben Tage abgefragt und aktualisiert. Das bedeutet, dass alle seit der letzten Abfrage veröffentlichten Werte verarbeitet werden und auch alle Werte der letzten sieben Tage verarbeitet werden. Dies ist notwendig, da die kürzlich auf ENTSO-E veröffentlichten Daten einer Revision unterliegen und es aufgrund von Ausfällen gelegentlich zu Verzögerungen kommt, bis die Erzeugungsdaten auf dem Portal erscheinen. Von 2:00 bis 3:00 Uhr (UTC) wird die reguläre Abfrage unterbrochen und alle Erzeugungsdaten werden neu abgefragt, um sicherzustellen, dass auch alle älteren Daten verarbeitet werden, die inzwischen revidiert wurden.

## Erzeugungsprognosen

Die aktuellen und vergangenen Erzeugungsdaten, die den Zeitraum vom 1.1.2024 bis etwa zum heutigen Zeitpunkt abdecken (unter der Annahme, dass die neuesten Daten ohne Verzögerung veröffentlicht wurden), werden durch prognostizierte Erzeugungsdaten ergänzt. Die Erzeugungsprognosen stammen ebenfalls aus dem Transparenzportal von ENTSO-E. Dort stehen zwei Arten von Prognosen zur Verfügung:

- Prognosen zur Stromerzeugung aus Wind- und Solarenergie, aufgeschlüsselt nach Quellen (Solarenergie, Windenergie an Land usw.) (URL: https://transparency.entsoe.eu/generation/r2/dayAheadGenerationForecastWindAndSolar/show)
- Aggregierte Stromerzeugung, d. h. ein einzelner Wert, der die prognostizierte Summe der gesamten Stromerzeugung aus allen Quellen darstellt (https://transparency.entsoe.eu/generation/r2/dayAheadAggregatedGeneration/show)

In ihrer Rohform reichen diese Daten für unsere Analyse nicht aus: Während die Solar- und Windprognosen nach Energieträgern (Solar, Wind an Land, Wind auf See) aufgeschlüsselt sind und eine Auflösung von 15 Minuten aufweisen, beinhaltet die aggregierte Erzeugungsprognose lediglich den Gesamtwert der gesamten deutschen Erzeugung und liegt in einer Auflösung von 60 Minuten vor.

Um die realen Erzeugungsdaten zu ergänzen, verwenden wir einen Algorithmus, um aus dem Gesamtwert Werte für jede Energiequelle abzuleiten:

 - Zunächst konvertieren wir jeden Gesamtwert in vier 15-Minuten-Werte. Dann berechnen wir für jeden Zeitschritt die Resterzeugung (Gesamterzeugung – die Summe der Wind- und Solarerzeugung).
 - Anschließend verwenden wir eine eindimensionale Suche nach dem nächsten Nachbarn, um den Punkt in den historischen Daten mit dem ähnlichsten Restgenerationswert zu finden.
 - Anschließend ermitteln wir das Verhältnis der Gesamtstromerzeugung zu diesem Zeitpunkt zur Erzeugung jeder einzelnen Quelle.
 - Abschließend wenden wir diese Verhältnisse auf den Gesamtprognosewert an, um eine geschätzte Erzeugungsprognose für jede der verbleibenden Quellen zu erhalten.
 
Auf diese Weise können wir geschätzte zukünftige Werte für die Erzeugung, die Emissionen und den deutschen Gesamtemissionsfaktor anzeigen. Da die von uns gesammelten Redispatch-Daten geplante zukünftige Redispatches enthalten, können wir auch geschätzte zukünftige Werte für die zonalen Emissionsfaktoren für den Norden und den Süden anzeigen, da diese sowohl auf den veröffentlichten Redispatch-Daten als auch auf den Erzeugungs- und Emissionsdaten basieren.

### Zeitrahmen der Prognosen

- „Day-ahead“: Veröffentlichung ca. 18:00 Uhr mit Werten bis 23:45 Uhr des Folgetages.
- „Intraday“ und „aktuell“: Diese Prognosen werden in unregelmäßigen Abständen veröffentlicht und korrigieren die Day-Ahead-Werte, erweitern diese jedoch nicht.
- Die Prognosewerte werden durch reale Erzeugungswerte ersetzt, sobald diese eintreffen.

Aufgrund des Veröffentlichungsrhythmus stehen Prognosedaten somit mindestens bis 23:45 Uhr des aktuellen Tages und maximal bis 23:45 Uhr des Folgetages zur Verfügung.

## Emissionsfaktoren

Die Emissionsfaktoren (kgCO2/MWh) für die einzelnen Quellen sind der DIN SPEC 91410-2 entnommen:

- Biomasse: 123
- Braunkohle: 1075
- Erdgas": 420
- Steinkohle: 933
- Mineralöl: 1098
- Geothermie: 5
- Pumpspeicher: 5
- Wasserkraft (Laufwasser): 3
- Wasserspeicher: 3
- Marine: 3
- Kernenergie: 35
- Sonstige Erneuerbare Energien: 5
- Photovoltaik: 38
- Abfall: 1098
- Windenergie (Offshore-Anlage): 9
- Windenergie (Onshore-Anlage): 9
- Sonstige konventionelle Energien: 1098

Bei der Berechnung der gesamten deutschen Emissionswerte je Quelle werden diese Emissionsfaktoren unverändert verwendet: Erzeugungswert Quelle (in MWh) * Emissionsfaktor Quelle = Emissionswert. Diese werden auch unverändert bei der Berechnung des deutschen Emissionsfaktors verwendet.

Bei der Berechnung der zonalen Emissionsfaktoren werden die DIN-Emissionsfaktoren reduziert, wenn die Erzeugungsanlage eine Anlage der Kraft-Wärme-Kopplung ist. Der Multiplikator beträgt 0,625. Diese reduzierten Emissionsfaktoren (ursprünglicher Emissionsfaktor * 0,625) werden bei der Berechnung der Emissionen für eine bestimmte Zone im Falle eines konventionellen Energie-Redispatches verwendet (die Redispatch-Daten werden nach Erzeugungsanlagen aufgeschlüsselt, so dass neben der Energiequelle auch festgestellt werden kann, ob die Anlage zum Heizen genutzt wird). Bei der Berechnung der zonalen Emissionsfaktoren werden die DIN-Emissionsfaktoren
verringert, wenn die Anlage zur Kraft-Wärmekopplung (KWK) genutzt wird. Der Abschlag erfolgt durch Multiplikation mit dem Faktor 0,625. Diese reduzierten Emissionsfaktoren (ursprünglicher Emissionsfaktor * 0,625) werden bei der Berechnung der Emissionen für eine bestimmte Zone im Falle eines konventionellen Energie-Redispatches verwendet (die Redispatch-Daten werden nach
Erzeugungsanlagen aufgeschlüsselt, so dass neben der Energiequelle auch festgestellt werden kann, ob die Anlage über eine Wärmeauskopplung verfügt (KWK-Anlage)). Der Faktor 0,625 ergibt sich aus der Anwendung der sog. Wirkungsgradmethode unter Annahme typischer Stromkennzahlen und Wirkunggrade für KWK-Anlagen (https://www.umweltbundesamt.de/sites/default/files/medien/publikation/long/3476.pdf) 

## Emissionen

Die Emissionswerte werden pro Energieträger in 15-Minuten-Auflösung angezeigt. Sie werden berechnet, indem die Erzeugungswerte mit den entsprechenden DIN-Emissionsfaktoren multipliziert werden. Die Emissionsdaten hängen direkt von der Verfügbarkeit der Erzeugungsdaten ab: Wenn Erzeugungsdaten für einen bestimmten Zeitpunkt vorliegen, dann liegen für diesen Zeitpunkt auch Emissionsdaten vor. Wir zeigen auch geschätzte zukünftige Emissionen anhand der geschätzten zukünftigen Erzeugungsdaten an. Immer wenn Erzeugungsdaten aktualisiert werden, werden auch die entsprechenden Emissionsdaten aktualisiert.

## Redispatch

Redispatch-Daten werden über die Web-API von netztranzparenz.de (URL: https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsfuehrung/Redispatch) erhoben. Die `MITTLERE_LEISTUNG_MW` von jeder Redispatch-Maßnahme werden in aggregierter Form angezeigt. Die von netztransparenz.de bereitgestellten Daten enthalten zwar den Namen der betroffenen Anlage, jedoch keine detaillierten Informationen wie die Energiequelle (Solar, Onshore-Wind usw.) oder den Anlagentyp (z. B. Heizkraftwerk - Erdgas). Da diese Informationen zur Bestimmung der zonalen Emissionsfaktoren erforderlich sind, ergänzen wir die Redispatch-Daten mit unseren eigenen Energieanlagen-Daten. Abgesehen von der Aggregation für Anzeigezwecke werden die Redispatch-Daten nicht verändert.

## Deutscher nationaler Emissionsfaktor

Der bundesweite Emissionsfaktor wird aus den Erzeugungsdaten (umgerechnet in MWh) und den oben beschriebenen DIN-Emissionsfaktoren berechnet. Er ist das gewichtetes arithmetisches Mittel der Emissionsfaktoren, gewichtet nach der Erzeugung je Energieträger.

## Zonale Emissionsfaktoren

Die zonalen Emissionsfaktoren für die Nord- und Südzonen werden nach folgenden Regeln angezeigt:

Für die ausgewählte Zone:

Der zonale Emissionsfaktor ist 0, wenn alle der folgenden Punkte zutreffen:
- Es gibt _mindestens einen_ EE-Redispatch mit der Richtung „Wirkleistungseinspeisung reduzieren“ in der ausgewählten Zone.
- Es gibt _keine_ konventionellen Redispatches mit der Richtung „Wirkleistung erhöhen“ in der ausgewählten Zone.

Der zonale Emissionsfaktor wird auf Basis der konventionellen Redispatches in der ausgewählten Zone berechnet, wenn alle der folgenden Punkte zutreffen:
- Es gibt _mindestens einen_ konventionellen Redispatch mit der Richtung „Wirkleistung erhöhen“ in der ausgewählten Zone.
- Es gibt _keinen_ konventionellen Redispatch mit der Richtung „Wirkleistung erhöhen“ in der Gegenzone.
- Es gibt _mindestens einen_ EE-Redispatch mit der Richtung „Wirkleistungseinspeisung reduzieren“ in der Gegenzone.
 
(Einzelheiten zur Berechnung des zonalen Emissionsfaktors finden Sie weiter unten.)

In allen anderen Fällen wird der deutsche Emissionsfaktor angezeigt (siehe oben „Deutscher nationaler Emissionsfaktor“).

Der angezeigte zonale Emissionsfaktor, wenn in einer Zone konventioneller Redispatch stattfindet, wird auf Basis unserer angereicherten Redispatch-Daten berechnet, die neben der Erzeugung (umgerechnet in MWh) auch den Energieträger und die Angabe enthalten, die DIN-Emissionsfaktoren und  bei KWK-Anlagen einem Multiplikator, der sich aus der Anwedung des Wirkungsgradverfahrens ergibt.. Die angezeigten Werte sind die gewichteten arithmetischen Mitteln der Emissionsfaktoren, gewichtet mit der Erzeugung aus den jeweiligen konventionellen Redispatches.

### Beispiel: Der zonale Emissionsfaktor im Norden beträgt 0 kgCO2/MWh

Der zonale Emissionsfaktor in der Nordzone beträgt am 23. Dezember 2024 von 10:00 bis 10:15 UTC 0 kgCO2/MWh. Der Grund:

1. Es gibt _keine_ konventionellen Redispatches mit der Anweisung „Wirkleistung erhöhen“ in der Nordzone.
2. Es gibt _mindestens einen_ EE-Redispatch mit der Anweisung „Wirkleistungseinspeisung reduzieren“ in der Nordzone. In diesem Fall gibt es mehrere, darunter:
	- OWP UW Dörpen-West Windenergie (Offshore-Anlage)
	- EE Niedersachsen Sonstige Erneuerbare Energien
	- WP Wilstermarsch Windenergie (Onshore-Anlage)
	- OWP UW Dörpen-West Windenergie (Offshore-Anlage)
	- OWP UW Emden-Ost Windenergie (Offshore-Anlage)
	- OWP UW Büttel Windenergie (Offshore-Anlage)
 
Da beide Bedingungen erfüllt sind, müssen die Emissionsfaktoren für die einzelnen Redispatches nicht berücksichtigt werden und der zonale Emissionsfaktor für den Norden beträgt einfach 0 kgCO2/MWh.

### Beispiel: Der zonale Emissionsfaktor im Süden ist größer als der nationale Emissionsfaktor

Der zonale Emissionsfaktor in der Südzone ist am 23. Dezember 2024 von 10:00 bis 10:15 UTC höher als der bundesdeutsche Emissionsfaktor. Der Grund:

1. Es gibt _keine_ konventionellen Redispatches mit Richtung „Wirkleistung erhöhen“ in der Nordzone.
2. Es gibt _mindestens einen_ EE-Redispatch mit Richtung „Wirkleistungseinspeisung reduzieren“ in der Nordzone (es gibt mehrere, zum Beispiel einen vom SHN-Cluster Süderdonn T411).
3. Es gibt konventionelle Redispatches mit Richtung „Wirkleistung erhöhen“ in der Südzone. (Beachten Sie, dass einer einzelnen Anlage möglicherweise mehrere Redispatches zugeordnet sind.)
	- Rheinhafen-Dampfkraftwerk Karlsruhe Block 8
		- 60,9375 MWh (243,75 mittlere Leistung MW)
		- Steinkohle 
		- KWK-Anlage 
		- Emissionsfaktor 583,125 kgCO2/MWh (933 kgCO2/MWh Steinkohle * 0,625 KWK-Anlage) 
	- Rheinhafen-Dampfkraftwerk Karlsruhe Block 8 
		- 111,215 MWh (444,86 mittlere Leistung MW) 
		- Steinkohle 
		- KWK-Anlage 
		- Emissionsfaktor 583,125 kgCO2/MWh (933 kgCO2/MWh Steinkohle * 0,625 KWK-Anlage) 
	- Großkraftwerk Mannheim Block 6 
		- 20,9425 MWh (83,77 mittlere Leistung MW) 
		- Steinkohle 
		- KWK-Anlage 
		- Emissionsfaktor 583,125 kgCO2/MWh (933 kgCO2/MWh Steinkohle * 0,625 KWK-Anlage) 
	- Heizkraftwerk Altbach/Deizisau GT B 
		- 14,75 MWh (59,0 mittlere Leistung MW) 
		- Erdgas 
		- KWK-Anlage 
		- Emissionsfaktor 262,5 (420 Erdgas * 0,625 KWK-Anlage) 
	- Heizkraftwerk Altbach/Deizisau GT C 
		- 20,75 MWh (83,0 mittlere Leistung MW) 
		- Erdgas 
		- KWK-Anlage 
		- Emissionsfaktor 262,5 kgCO2/MWh (420 kgCO2/MWh Erdgas * 0,625 KWK-Anlage) 
	- Heizkraftwerk Altbach/Deizisau Block 2 
		- 28,42 MWh (113,68 mittlere Leistung MW) 
		- Steinkohle 
		- KWK-Anlage 
		- Emissionsfaktor 583,125 kgCO2/MWh (933 kgCO2/MWh Steinkohle * 0,625 KWK-Anlage) 
	- Heizkraftwerk Altbach/Deizisau Block 2 
		- 33,9275 MWh (135,71 mittlere Leistung MW) 
		- Steinkohle 
		- KWK-Anlage 
		- Emissionsfaktor 583,125 kgCO2/MWh (933 kgCO2/MWh Steinkohle * 0,625 KWK-Anlage)
	
 Der zonale Emissionsfaktor ist das gewichtete arithmetische Mittel der Emissionsfaktoren, gewichtet nach der Erzeugung pro Energiequelle: 544 kgCO2/MWh. Der deutsche nationale Emissionsfaktor für diesen Zeitraum beträgt 204,27 kgCO2/MWh.

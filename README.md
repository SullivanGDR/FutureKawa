# FutureKawa — Console de Supervision IoT

Plateforme industrielle de supervision du stockage de café vert vert en grains. Elle agrège les données temps réel des modules IoT déployés dans des entrepôts au Brésil, en Colombie et en Équateur, déclenche des alertes qualité automatiques et offre une interface de gestion complète aux opérateurs.

---

## Prérequis

- [Docker](https://docs.docker.com/get-docker/) 24+ avec Docker Compose v2
- `make` (inclus sur Linux/macOS ; sur Windows : Git Bash, WSL, ou `winget install GnuWin32.Make`)
- Ports disponibles : `3000`, `5432`, `5050`, `8000`, `8080`, `1883`, `9001`

---

## Démarrage rapide

```bash
git clone https://github.com/ThibautHrm/FutureKawa.git
cd FutureKawa
make start
```

`make start` construit toutes les images et lance l'ensemble des services en arrière-plan. La première exécution prend environ 2–4 minutes (téléchargement des images de base et compilation du frontend Nuxt).

Une fois tous les services démarrés, les interfaces sont accessibles aux adresses suivantes :

| Service | URL | Identifiants |
|---|---|---|
| Console web | http://localhost:3000 | voir comptes ci-dessous |
| API REST (Brésil) | http://localhost:8000/docs | — |
| pgAdmin | http://localhost:5050 | `admin@futurekawa.com` / `admin` |
| Jenkins CI/CD | http://localhost:8080 | `admin` / `admin` |
| MQTT Broker | `localhost:1883` | — |

---

## Comptes de démonstration

| Rôle | Email | Mot de passe | Périmètre |
|---|---|---|---|
| Administrateur | `admin@futurekawa.com` | `admin` | Tous les pays |
| Employé Brésil | `bresil@futurekawa.com` | `kawa` | Brésil uniquement |
| Employé Colombie | `colombie@futurekawa.com` | `kawa` | Colombie uniquement |
| Employé Équateur | `equateur@futurekawa.com` | `kawa` | Équateur uniquement |

---

## Architecture des services

Le projet est entièrement conteneurisé. Voici le rôle de chaque service Docker :

```
postgres          — Base de données PostgreSQL 16 (données persistées dans un volume)
db-init           — Initialise le schéma et injecte les données de seed au premier démarrage
backend           — API FastAPI (Python) exposée sur :8000
frontend          — Application Nuxt 4 (SSR) exposée sur :3000
mqtt-broker       — Broker Eclipse Mosquitto 2 (MQTT :1883, WebSocket :9001)
mqtt-bridge       — Pont Python : consomme le topic MQTT → POST vers l'API REST
iot-simulator     — Simule les capteurs IoT, publie une mesure toutes les 120 secondes
pgadmin           — Interface graphique PostgreSQL exposée sur :5050
jenkins           — Serveur CI/CD Jenkins LTS exposé sur :8080
```

---

## Commandes `make` disponibles

```bash
make start          # Build + lancement de tous les services
make stop           # Arrêt (les volumes sont conservés)
make clean          # Arrêt + suppression des volumes (remet la base à zéro)
make restart        # Équivalent à stop puis start
make logs           # Affiche les logs en temps réel (Ctrl+C pour quitter)
make test           # Lance les tests backend et frontend
make test-backend   # Tests Python uniquement (pytest)
make test-frontend  # Tests TypeScript uniquement (vitest)
```

> **Attention** : `make clean` supprime tous les volumes Docker, y compris la base de données. Toutes les données seront perdues et le schéma sera réinitialisé au prochain `make start`.

---

## Développement local (sans Docker)

### Backend

```bash
cd FutureKawaBresil_API
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

export DATABASE_URL="postgresql+asyncpg://postgres:root@localhost:5432/MSPR_TPRE814_Bresil"
export NOM_PAYS="Brésil"
python reset_db.py                 # Initialise la base
uvicorn app.main:app --reload --port 8000
```

L'API sera disponible sur http://localhost:8000 et la documentation Swagger sur http://localhost:8000/docs.

### Frontend

```bash
cd FutureKawa_Frontend
npm install

# Créer un fichier .env avec les URLs des APIs
NUXT_API_BRESIL_URL=http://localhost:8000/api/v1
NUXT_API_COLOMBIE_URL=http://localhost:8001/api/v1
NUXT_API_EQUATEUR_URL=http://localhost:8002/api/v1

npm run dev
```

Le frontend sera disponible sur http://localhost:3000.

### Simulateur IoT

```bash
cd iot-simulator
pip install paho-mqtt
MQTT_BROKER=localhost MQTT_PORT=1883 python simulator.py
```

Le simulateur publie une mesure synthétique toutes les 120 secondes sur le topic `futurekawa/bresil/mesures`.

---

## Pipeline CI/CD Jenkins

Au premier démarrage, Jenkins est préconfiguré via JCasC (`jenkins/casc.yaml`). Le pipeline `FutureKawa-Pipeline` est disponible dans l'interface dès le lancement.

Étapes du pipeline :

1. **Checkout** — récupération du code source
2. **Build** — construction des images Docker backend et frontend
3. **Tests Backend** — exécution de pytest avec rapport JUnit
4. **Tests Frontend** — exécution de vitest avec rapport JUnit
5. **Lint** — analyse statique flake8 du code Python
6. **Package** — mise en archive des artefacts

Pour lancer un build : http://localhost:8080 → `FutureKawa-Pipeline` → **Lancer un build**.

---

## Structure du projet

```
FutureKawa/
├── FutureKawaBresil_API/     # API FastAPI (Python)
│   ├── app/
│   │   ├── main.py           # Point d'entrée, routers, workers cron
│   │   ├── models/           # Modèles SQLAlchemy
│   │   ├── routes/           # Endpoints REST par domaine
│   │   └── utils/            # Auth, mail, sécurité
│   ├── tests/                # Tests pytest
│   └── reset_db.py           # Script d'initialisation et seed
├── FutureKawa_Frontend/      # Application Nuxt 4 (Vue 3 / TypeScript)
│   ├── app/
│   │   ├── pages/            # Pages de l'application
│   │   ├── composables/      # Logique réutilisable (auth, état pays, dialogs)
│   │   └── layouts/          # Layout principal avec sidebar
│   └── server/api/           # BFF gateway : proxy vers les APIs régionales
├── iot-simulator/            # Simulateur de capteurs (Python + paho-mqtt)
├── mqtt-bridge/              # Pont MQTT → API REST (Python)
├── mosquitto/config/         # Configuration du broker MQTT
├── jenkins/                  # Dockerfile Jenkins + JCasC
├── docker-compose.yml
└── Makefile
```

---

## Résolution de problèmes courants

**Le frontend affiche "Impossible de charger les données"**
Le backend n'est peut-être pas encore prêt. Attendre 30–60 secondes supplémentaires après `make start` puis rafraîchir. Vérifier avec `make logs`.

**Le port 8000 ou 3000 est déjà utilisé**
Arrêter le service qui occupe le port ou modifier les mappings dans `docker-compose.yml`.

**Remettre la base de données à zéro**
```bash
make clean && make start
```

**Voir les logs d'un service spécifique**
```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f mqtt-bridge
```

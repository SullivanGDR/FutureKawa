# FutureKawa — Documentation Technique du Projet

> Document de référence exhaustif couvrant l'architecture, le fonctionnement, les composants et les procédures d'exploitation de la plateforme FutureKawa.

---

## 1. Vue d'ensemble du projet

FutureKawa est une console de supervision industrielle dédiée au suivi des conditions de stockage du café vert. L'objectif central de la plateforme est de garantir la qualité des grains de café tout au long de leur séjour dans les entrepôts de trois pays producteurs : le **Brésil**, la **Colombie** et l'**Équateur**.

Le système assure deux responsabilités fondamentales. D'un côté, il suit en temps réel les conditions environnementales (température et humidité) à l'intérieur de chaque entrepôt grâce à des capteurs IoT connectés via le protocole MQTT. De l'autre, il gère la traçabilité des lots de café en appliquant une règle de rotation FIFO (First In, First Out) : tout lot stocké depuis plus de 365 jours est automatiquement marqué périmé et le responsable local en est notifié par e-mail.

L'architecture est conçue pour être **multi-régions**. Chaque pays opère son propre nœud d'API indépendant, et le frontend consolide les données de l'ensemble des nœuds en une interface unifiée. Cette séparation permet à chaque région de fonctionner de manière autonome, même en cas d'indisponibilité des autres.

---

## 2. Architecture globale

La plateforme repose sur neuf services Docker qui communiquent entre eux au sein d'un réseau interne Docker Compose. L'ensemble du projet se lance par une seule commande depuis la racine du dépôt.

**PostgreSQL 16** est la base de données relationnelle principale. Elle est initialisée au premier démarrage par un service dédié (`db-init`) qui exécute le script `reset_db.py`, lequel applique le schéma SQL et insère des données de démonstration réalistes.

**Le backend FastAPI** (port 8000) constitue le cœur métier. Il expose l'API REST sous le préfixe `/api/v1` et démarre en attendant que le service `db-init` se soit terminé avec succès.

**Le frontend Nuxt** (port 3000) sert la console de supervision. Il joue un rôle de passerelle (BFF — Backend for Frontend) : il agrège les données provenant des trois APIs régionales avant de les transmettre au navigateur.

**Eclipse Mosquitto** (port 1883 TCP, port 9001 WebSocket) est le broker MQTT qui reçoit les messages des capteurs IoT.

**Le MQTT Bridge** est un service Python qui souscrit au topic MQTT `futurekawa/bresil/mesures` et transmet chaque message reçu à l'API FastAPI via une requête HTTP POST sur l'endpoint `/api/v1/releves/`.

**Le simulateur IoT** publie toutes les 10 secondes des mesures fictives de température et d'humidité pour trois modules prédéfinis (`br-santos-01`, `br-rio-02`, `col-medellin-01`).

**pgAdmin** (port 5050) est disponible pour l'administration visuelle de la base de données.

**Jenkins** (port 8080) orchestre le pipeline CI/CD et est accessible depuis un navigateur.

---

## 3. Stack technique

### Backend
Le backend est développé en **Python 3** avec le framework **FastAPI**. Toutes les opérations de base de données sont asynchrones grâce à **SQLAlchemy 2.0** en mode async associé au driver **asyncpg** pour PostgreSQL. La validation des données entrantes et sortantes passe par des schémas **Pydantic v2**. La configuration de l'application est gérée par **pydantic-settings** et peut être surchargée via un fichier `.env`. Les migrations de schéma sont gérées par **Alembic**, bien que dans l'état actuel le schéma soit recréé à chaque démarrage via `reset_db.py`. L'envoi d'e-mails s'appuie sur **fastapi-mail** connecté à un serveur SMTP Mailtrap (sandbox).

### Frontend
Le frontend est développé avec **Nuxt 4** (Vue 3) et **TypeScript**. Les graphiques de télémétrie utilisent **Chart.js** via le wrapper **vue-chartjs**, complété du plugin **chartjs-plugin-annotation** pour afficher les lignes de seuils directement sur les graphes. Les icônes proviennent de la bibliothèque **lucide-vue-next**. Les tests unitaires côté frontend sont écrits avec **Vitest**.

### Infrastructure
Tout l'environnement est conteneurisé avec **Docker** et orchestré via **Docker Compose**. Le pipeline CI/CD est défini dans un **Jenkinsfile** déclaratif et s'exécute au sein de Jenkins lui-même, déployé en container. La qualité du code Python est vérifiée par **flake8** avec une configuration permissive (exit-zero, pour ne pas bloquer le build sur des avertissements de style).

### Communication IoT
Le protocole de messagerie IoT est **MQTT v5** via le broker **Eclipse Mosquitto 2**. Le client Python utilise la bibliothèque **paho-mqtt**.

---

## 4. Infrastructure Docker Compose

Le fichier `docker-compose.yml` à la racine du projet définit les neuf services avec leurs dépendances, leurs variables d'environnement et leurs health checks.

L'ordre de démarrage est garanti par les conditions `depends_on`. PostgreSQL doit passer son health check (`pg_isready`) avant que `db-init` puisse s'exécuter. `db-init` doit se terminer avec succès avant que le backend ne démarre. Le backend doit passer son health check HTTP avant que le frontend ne démarre.

Les volumes Docker nommés `pgdata`, `mosquitto-data`, `mosquitto-log` et `jenkins-data` assurent la persistance des données entre les redémarrages. Lors d'un `docker compose down`, ces volumes sont conservés par défaut. Pour repartir d'un état propre (réinitialisation complète), il faut ajouter le flag `-v` : `docker compose down -v`.

Le frontend reçoit trois variables d'environnement lui indiquant l'URL de chaque API régionale : `NUXT_API_BRESIL_URL`, `NUXT_API_COLOMBIE_URL` et `NUXT_API_EQUATEUR_URL`. Dans la configuration Docker Compose fournie, seul le Brésil dispose d'un backend local (port 8000). Les deux autres nœuds pointent vers `localhost:8001` et `localhost:8002`, qui ne sont pas définis dans le compose. Le frontend gère cette situation gracieusement : quand un nœud est inaccessible, il retourne un tableau vide ou des valeurs par défaut, et affiche le nœud comme "Hors ligne" dans l'interface.

---

## 5. Base de données — Schéma relationnel

La base s'appelle `MSPR_TPRE814_Bresil` et contient sept tables.

**`configuration_pays`** est la table de référence des paramètres régionaux. Sa clé primaire est `nom_pays` (ex: "Brésil"). Elle stocke l'e-mail du responsable local ainsi que les seuils climatiques idéaux : température idéale, humidité idéale, et leurs tolérances respectives. Les seuils effectifs sont calculés dynamiquement en Python comme `temp_ideale ± tolerance_temp`. Au démarrage, trois entrées sont insérées : Brésil (29°C ± 3°C, 55% ± 2%), Colombie (26°C ± 3°C, 80% ± 2%), Équateur (31°C ± 3°C, 60% ± 2%).

**`utilisateurs`** contient les comptes d'accès à la console. Chaque utilisateur possède un e-mail, un nom, un hash de mot de passe SHA-256, un rôle (`admin` ou `employe`) et une clé étrangère optionnelle vers `configuration_pays.nom_pays`. Un utilisateur `employe` est rattaché à un seul pays ; un `admin` n'est rattaché à aucun pays et voit toutes les données.

**`entrepot`** représente les sites de stockage physiques. La table est volontairement simple : un identifiant auto-incrémenté et un nom. Les entrepôts de démonstration sont "Hub Central Santos" (id 1), "Rio Terminal A" (id 2), "Medellin Depot" (id 3) et "Quito Silos" (id 4).

**`lot`** représente une unité de traçabilité de café vert. L'identifiant du lot est une chaîne libre (ex: `LOT-BR-001`), définie par l'opérateur. Chaque lot référence un entrepôt par clé étrangère et possède une date de stockage et un statut parmi trois valeurs : `conforme`, `en alerte` ou `périmé`. La suppression d'un entrepôt propage une suppression en cascade sur ses lots (`ON DELETE CASCADE`).

**`module_iot`** représente un capteur physique. Son identifiant est une chaîne libre (ex: `br-santos-01`), significative pour les opérateurs. Chaque module est associé à un entrepôt et porte un statut de connexion : `actif` ou `inactif`. Ce statut est mis à jour automatiquement par le système en fonction de la réception ou de l'absence de mesures MQTT.

**`releve_mesure`** stocke chaque mesure individuelle transmise par un capteur. Une entrée contient la date/heure (avec timezone), la température et l'humidité en décimaux (5 chiffres dont 2 après la virgule), et la référence au module source. C'est la table qui grandit le plus rapidement — le simulateur y insère une entrée toutes les 10 secondes par module actif.

**`alerte`** centralise tous les incidents détectés par le système. Une alerte référence soit un lot (alertes de péremption), soit un module (alertes de conditionnement ou de connexion). Le champ `type_alerte` prend trois valeurs : `Conditionnement`, `Péremption` ou `Perte de connexion`. Le champ booléen `traitee` passe à `true` lorsque l'opérateur acquitte l'alerte depuis la console.

---

## 6. Backend — Structure du code

Le backend est organisé selon le pattern classique FastAPI avec séparation stricte des couches.

`main.py` est le point d'entrée. Il instancie l'application FastAPI, configure le middleware CORS (origines autorisées : `http://localhost:3000`), monte le routeur principal sous `/api/v1` et démarre les tâches de fond via le gestionnaire de cycle de vie (`lifespan`).

`app/config.py` définit la classe `Settings` héritant de `BaseSettings`. Les valeurs sont lues depuis les variables d'environnement ou le fichier `.env`. Les paramètres critiques sont `DATABASE_URL` (obligatoire), `NOM_PAYS` (défaut "Brésil") et la configuration SMTP pour Mailtrap.

`app/database.py` crée le moteur SQLAlchemy asynchrone et définit la fonction `get_db()` utilisée comme dépendance FastAPI pour injecter une session dans chaque endpoint. La session gère automatiquement le commit en cas de succès ou le rollback en cas d'exception.

`app/models/` contient les modèles SQLAlchemy (une classe par table). `app/schemas/` contient les schémas Pydantic pour la validation des données entrantes (`Create`) et la sérialisation des données sortantes (`Response`). `app/crud/` contient les fonctions d'accès à la base de données. Cette séparation garantit que les endpoints restent minces et délèguent la logique de persistance aux fonctions CRUD.

---

## 7. Backend — API REST

Tous les endpoints sont préfixés par `/api/v1`. La documentation interactive Swagger est disponible à l'adresse `http://localhost:8000/docs` lorsque le backend est démarré.

**Authentification** (`/api/v1/auth/login`, POST) : reçoit un e-mail et un mot de passe en clair, vérifie le hash SHA-256 en base, et retourne les informations de l'utilisateur (id, nom, e-mail, rôle, pays). Il n'y a pas de token JWT — la session est gérée côté frontend dans le localStorage.

**Configuration pays** (`/api/v1/configuration-pays`, GET et POST) : récupère ou met à jour les seuils climatiques d'un pays. Le POST effectue un upsert (insertion ou mise à jour selon que le pays existe déjà).

**Entrepôts** (`/api/v1/entrepots`) : opérations CRUD classiques. GET liste tous les entrepôts, GET `/{id}` récupère un entrepôt précis, POST crée, DELETE supprime.

**Lots** (`/api/v1/lots`) : opérations CRUD avec en plus GET `/entrepot/{entrepot_id}` pour filtrer par entrepôt et PATCH `/{lot_id}/statut` pour changer uniquement le statut d'un lot.

**Modules IoT** (`/api/v1/modules`) : même structure que les lots, avec en plus PATCH `/{module_id}/statut` pour forcer le statut de connexion.

**Relevés de mesure** (`/api/v1/releves`) : le POST est l'endpoint le plus important fonctionnellement — il déclenche la chaîne de détection d'anomalies décrite ci-dessous. GET liste tous les relevés, GET `/module/{module_id}` filtre par capteur.

**Alertes** (`/api/v1/alertes`) : GET liste toutes les alertes, GET `/{id}/acquitter` (POST) tente d'acquitter une alerte selon des règles métier précises, GET `/module/{module_id}`, GET `/lot/{lot_id}`, GET `/entrepot/{entrepot_id}` pour les filtres.

---

## 8. Backend — Système de détection d'alertes

Le système génère trois types d'alertes selon des déclencheurs différents.

### Alerte de Conditionnement (déclenchée à la réception d'un relevé)

Lorsqu'un relevé est reçu via POST `/api/v1/releves/`, l'endpoint effectue les opérations suivantes en séquence. Il crée d'abord l'entrée en base. Ensuite, si le module est connu et était précédemment inactif, il le repasse à l'état `actif` (réactivation automatique au retour du signal). Puis il charge la configuration du pays et compare les valeurs mesurées aux seuils. Si la température est hors de l'intervalle `[temp_ideale - tolerance_temp, temp_ideale + tolerance_temp]` ou si l'humidité est hors de `[hum_ideale - tolerance_hum, hum_ideale + tolerance_hum]`, il crée une alerte de type `Conditionnement`, envoie un e-mail HTML au responsable, et passe tous les lots `conformes` de l'entrepôt concerné à l'état `en alerte`.

### Alerte de Péremption (déclenchée par le worker toutes les heures)

La tâche `check_expired_lots` s'exécute toutes les heures en arrière-plan. Elle charge tous les lots dont le statut n'est pas déjà `périmé`, calcule leur âge en jours depuis `date_stockage`, et pour chaque lot dépassant 365 jours, le marque `périmé` et crée une alerte `Péremption` si aucune alerte active de ce type n'existe déjà pour ce lot. Les lots nouvellement périmés sont compilés en un rapport envoyé par e-mail au responsable. Cette alerte est **irréversible** : il est impossible de l'acquitter depuis l'interface, et le lot reste définitivement marqué périmé.

### Alerte de Perte de connexion (déclenchée par le worker toutes les 30 secondes)

La tâche `check_module_connections` s'exécute toutes les 30 secondes. Pour chaque module, elle récupère le relevé le plus récent. Si aucun relevé n'a été reçu depuis plus de 30 minutes (ou si le module n'a jamais envoyé de mesure), et si le module était encore marqué `actif`, elle le passe à `inactif` et crée une alerte `Perte de connexion`. L'ensemble des modules nouvellement détectés hors ligne est compilé dans un seul e-mail récapitulatif.

### Règles d'acquittement

L'acquittement d'une alerte via POST `/api/v1/alertes/{id}/acquitter` suit des règles strictes. Une alerte `Péremption` ne peut jamais être acquittée. Une alerte `Conditionnement` ne peut être acquittée que si la dernière mesure du module concerné est revenue dans les seuils — l'API vérifie cette condition en temps réel avant d'autoriser le traitement. Quand une alerte de conditionnement est acquittée avec succès, tous les lots `en alerte` de l'entrepôt correspondant repassent à l'état `conforme`.

---

## 9. Backend — Service de notification par e-mail

Le service `app/services/mail.py` utilise fastapi-mail connecté à Mailtrap (serveur sandbox `sandbox.smtp.mailtrap.io`, port 2525). Les identifiants SMTP sont configurés dans le fichier `.env` du backend (`MAIL_USERNAME`, `MAIL_PASSWORD`).

Trois fonctions d'envoi sont définies, chacune générant un e-mail HTML structuré avec un en-tête FutureKawa sombre, un bandeau coloré selon la criticité (rouge pour les dérives climatiques, orange pour les pertes de connexion, ambre pour les péremptions), un tableau de données détaillé, et un bouton d'action pointant vers la console. Les e-mails sont adressés à l'e-mail du responsable configuré dans `configuration_pays` pour le pays concerné.

Si la configuration SMTP est incomplète ou si le serveur est inaccessible, l'envoi échoue silencieusement (le log affiche l'erreur, mais la requête API ne retourne pas d'erreur).

---

## 10. Pipeline IoT — MQTT

### Broker Mosquitto

Le fichier `mosquitto/config/mosquitto.conf` configure le broker Mosquitto avec deux listeners : le port 1883 en TCP classique pour les clients Python, et le port 9001 en WebSocket pour une éventuelle connexion depuis un navigateur. L'authentification anonyme est activée (`allow_anonymous true`), ce qui signifie que n'importe quel client peut publier ou souscrire sans credentials. La persistance des messages est activée.

### Simulateur IoT (`iot-simulator/simulator.py`)

Le simulateur est un script Python qui publie sur le topic `futurekawa/bresil/mesures` toutes les 10 secondes. Il simule trois capteurs : `br-santos-01` et `br-rio-02` (Brésil, cible 29°C / 55% HR) et `col-medellin-01` (Colombie, cible 26°C / 80% HR). À chaque cycle, il sélectionne aléatoirement un des trois modules et génère des valeurs dans les seuils de tolérance. La probabilité d'anomalie est actuellement fixée à 0% dans le code (`is_anomaly = random.random() < 0.00`), ce qui signifie que le simulateur produit uniquement des données conformes. Pour tester les alertes climatiques, il faut modifier ce seuil dans le code source ou injecter manuellement un relevé hors seuil via l'API.

Le payload publié est un JSON minimal : `{"temperature": 28.9, "humidite": 55.1, "id_module": "br-santos-01"}`.

### MQTT Bridge (`mqtt-bridge/bridge.py`)

Le bridge est un service Python permanent qui souscrit au topic `futurekawa/bresil/mesures` et fait le lien avec le backend FastAPI. À chaque message MQTT reçu, il parse le JSON du payload et envoie une requête HTTP POST synchrone vers `http://backend:8000/api/v1/releves/`. C'est ce POST qui déclenche toute la logique de détection d'anomalies côté backend. En cas d'échec de connexion à l'API, le bridge log l'erreur et continue d'écouter sans interrompre le service.

---

## 11. Frontend — Architecture Nuxt

Le frontend est une application Nuxt 4 avec rendu côté serveur (SSR). La structure suit les conventions Nuxt : les pages sont dans `app/pages/`, les composables dans `app/composables/`, le layout partagé dans `app/layouts/default.vue`, et les routes API serveur dans `server/api/`.

### Le Gateway multi-régions (`server/utils/gateway.ts`)

Ce fichier est la pièce centrale de l'architecture multi-pays. Il expose trois fonctions publiques. `getRegionalApiUrl(country)` résout l'URL de l'API pour un pays donné en lisant les variables d'environnement runtime (`apiBresilUrl`, `apiColombieUrl`, `apiEquateurUrl`). `fetchFromCountry(country, path, options)` effectue une requête vers un nœud régional précis. En cas de succès, il enrichit chaque objet de la réponse avec le champ `nom_pays` pour permettre l'identification de l'origine au niveau frontend. En cas d'erreur (nœud hors ligne), il retourne un tableau vide ou des valeurs par défaut selon le type de ressource demandée, sans propager l'exception. `fetchFromAllCountries(path)` interroge les trois nœuds en parallèle avec `Promise.all` et concatène les résultats en un seul tableau unifié.

### Routes API serveur (BFF)

Les fichiers dans `server/api/` constituent la couche BFF. Ils sont appelés par le frontend via `useFetch('/api/...')` et servent de proxy vers les APIs régionales. Par exemple, `server/api/lots/index.ts` appelle `fetchFromAllCountries('/lots')` pour retourner tous les lots de tous les pays au frontend. `server/api/lots/[id].ts` lit le paramètre `pays` de la query string pour savoir vers quel nœud router la requête. De cette manière, le navigateur ne communique jamais directement avec les APIs régionales — il passe toujours par le serveur Nuxt qui sert de passerelle sécurisée et agrégante.

---

## 12. Frontend — Authentification

L'authentification est gérée par le composable `useAuth.ts`. La connexion envoie un POST à `/api/auth/login` (route BFF) qui relaie vers `/api/v1/auth/login` du backend. En cas de succès, les informations de l'utilisateur sont stockées dans l'état global Vue (`useState`) et sauvegardées dans le `localStorage` pour la persistance entre les rafraîchissements de page.

Le middleware global `app/middleware/auth.global.ts` s'exécute côté client à chaque navigation. Si l'état utilisateur est vide, il tente de le restaurer depuis le localStorage via `checkAuth()`. Si après cette tentative l'utilisateur n'est toujours pas authentifié et que la page cible n'est pas `/login`, il redirige vers `/login`.

Le rôle de l'utilisateur influence l'interface de plusieurs façons. Un utilisateur `employe` rattaché à un pays voit ses données filtrées uniquement sur son pays et ne peut pas changer de filtre dans le header. Un utilisateur `admin` sans pays rattaché voit les données de tous les pays et peut filtrer par pays via les pills dans le header.

---

## 13. Frontend — Pages de la console

### Tableau de bord (`/`)

La page d'accueil affiche quatre indicateurs clés calculés à partir des données agrégées : le nombre total de lots enregistrés, le nombre de sites de stockage, le compteur d'alertes actives (avec indicateur LED rouge clignotant si non nul), et le taux de conformité des lots (pourcentage de lots au statut "conforme"). Elle affiche également les cinq dernières alertes non traitées dans un tableau, et un panneau de statut des nœuds API régionaux indiquant si chaque API est en ligne. Les données se rafraîchissent automatiquement toutes les 10 secondes.

### Gestion des lots (`/lots`)

Cette page liste tous les lots triés par ordre d'ancienneté croissante (FIFO), en affichant le rang FIFO, l'identifiant du lot, le pays, l'entrepôt, la date d'entrée, la date limite de péremption calculée (date d'entrée + 365 jours), la durée d'entreposage en jours, et le statut. Des filtres par recherche textuelle sur l'ID du lot, par entrepôt et par statut permettent d'affiner la liste. La pagination affiche 15 lots par page. Le bouton "Enregistrer un Lot" ouvre une modale pour créer un nouveau lot en choisissant son identifiant, son pays, son entrepôt et sa date d'entrée.

### Fiche lot (`/lots/[id]`)

La page de détail d'un lot affiche sa fiche complète (pays, entrepôt, dates, durée, statut), les modules IoT actifs dans son entrepôt avec leur statut de connexion, un graphique de télémétrie Chart.js affichant les courbes de température et d'humidité avec les lignes de seuil en pointillés, et l'historique de toutes les alertes liées à ce lot avec la possibilité d'acquitter celles qui le permettent. Le pays d'appartenance du lot est transmis via le paramètre `?pays=` dans l'URL, permettant au BFF de router vers le bon nœud régional.

### Entrepôts (`/parc`)

Liste tous les entrepôts avec leur ID, leur nom, leur zone géographique, le nombre de lots actuellement en stock et le nombre de modules IoT déployés. Permet d'ajouter un nouvel entrepôt via une modale ou d'en supprimer un existant (avec confirmation).

### Modules IoT (`/modules`)

Deux vues coexistent dans cette page. La vue liste présente un inventaire de tous les modules avec leur statut de connexion (indicateur LED vert/rouge), leur entrepôt, la dernière température et humidité mesurées (avec indication visuelle si hors seuil), et la date du dernier signal. La vue détail d'un module, accessible en cliquant "Inspecter", montre la fiche technique du capteur, ses deux dernières valeurs comparées aux seuils, un graphique de télémétrie complet avec annotations, et la liste de ses alertes actives. Un historique des alertes traitées est accessible dans une modale. Les données se rafraîchissent toutes les 15 secondes. Il est également possible d'enregistrer un nouveau module depuis cette page.

### Journal d'alertes (`/alertes`)

Présente l'ensemble des alertes de la plateforme dans un tableau paginé (10 par page), trié par date décroissante. Les compteurs en haut de page indiquent le nombre d'alertes climatiques et d'alertes de péremption. Chaque alerte affiche son type (badge rouge pour "Conditionnement", badge orange pour les autres), sa source (lot ou module), sa description et son statut. Le bouton "Acquitter" est absent pour les alertes de péremption (irréversibles) et désactivé si les mesures sont encore hors seuil.

### Paramètres (`/parametres`)

Permet de visualiser et modifier la configuration climatique de chaque pays. Le formulaire de gauche permet de sélectionner un pays, de modifier sa température idéale, son humidité idéale, leurs tolérances respectives et l'e-mail du responsable. Le panneau de droite affiche les configurations actuellement en vigueur pour les trois pays avec leur statut de connexion.

---

## 14. CI/CD — Pipeline Jenkins

Le pipeline est défini dans `Jenkinsfile` à la racine du projet et s'exécute en cinq étapes.

L'étape **Checkout** récupère le code source depuis le gestionnaire de versions.

L'étape **Build** construit les images Docker du backend et du frontend via `docker compose build`. Les deux images sont nommées `futurekawa-backend` et `futurekawa-frontend`.

L'étape **Tests Backend** démarre un conteneur temporaire à partir de l'image backend et exécute les tests Pytest. Les résultats sont exportés au format JUnit XML dans `/results/` puis copiés sur l'hôte Jenkins dans `test-results/backend-junit.xml`. Le conteneur est supprimé après l'export.

L'étape **Tests Frontend** suit le même pattern pour les tests Vitest. L'image frontend exécute `npm run test:ci` qui génère un fichier JUnit XML.

L'étape **Qualité flake8** analyse le code Python avec flake8 en mode `exit-zero`, ce qui signifie que les violations de style ne font pas échouer le build mais sont reportées en log.

L'étape **Package** tague les images construites avec le numéro de build Jenkins (`futurekawa-backend:42` par exemple) pour la traçabilité.

En post-traitement, Jenkins archive les fichiers XML de tests et nettoie les conteneurs temporaires. Le pipeline ne fait pas de déploiement automatique — l'étape de déploiement n'est pas encore implémentée.

---

## 15. Démarrage du projet

### Prérequis

Docker Desktop doit être installé et en cours d'exécution. Le projet n'a pas d'autre dépendance à installer sur la machine hôte.

### Démarrage complet

Depuis la racine du dépôt `D:/FutureKawa/FutureKawa/`, la commande suivante démarre l'ensemble de la plateforme :

```bash
docker compose up -d
```

Docker Compose construira les images manquantes, démarrera les services dans l'ordre correct grâce aux health checks, et initialisera la base de données avec les données de démonstration. L'opération prend environ 2 à 3 minutes au premier lancement (construction des images).

Pour vérifier que tous les services sont opérationnels :

```bash
docker compose ps
```

Tous les services doivent afficher l'état `running` ou `healthy`.

### Accès aux interfaces

La console de supervision est accessible à l'adresse `http://localhost:3000`. La documentation API Swagger du backend est disponible à `http://localhost:8000/docs`. L'administration de la base de données via pgAdmin est accessible à `http://localhost:5050` avec les identifiants `admin@futurekawa.com` / `admin`. Jenkins est disponible à `http://localhost:8080`.

### Arrêt et réinitialisation

Pour arrêter tous les services sans perdre les données : `docker compose down`. Pour arrêter et supprimer toutes les données (volumes inclus) afin de repartir d'un état propre : `docker compose down -v`.

---

## 16. Comptes utilisateurs de démonstration

La base de données est initialisée avec quatre comptes utilisateurs. Le mot de passe de tous les comptes est `kawa`, à l'exception du compte administrateur dont le mot de passe est `admin`.

Le compte `admin@futurekawa.com` (mot de passe `admin`) possède le rôle `admin` et n'est rattaché à aucun pays. Il voit l'ensemble des données de toutes les régions et peut filtrer par pays depuis la barre supérieure de l'interface.

Le compte `bresil@futurekawa.com` (mot de passe `kawa`) possède le rôle `employe` rattaché au Brésil. L'interface se filtrera automatiquement sur les données brésiliennes à sa connexion.

Le compte `colombie@futurekawa.com` (mot de passe `kawa`) et le compte `equateur@futurekawa.com` (mot de passe `kawa`) fonctionnent de la même manière pour leurs pays respectifs.

---

## 17. Données de démonstration

Au démarrage, le script `database_setup.sql` insère un ensemble de données représentatif pour illustrer les différents états du système.

Quatre entrepôts sont créés : "Hub Central Santos" et "Rio Terminal A" au Brésil, "Medellin Depot" en Colombie (qui correspond aussi à col-medellin-01 dans le simulateur), et "Quito Silos" en Équateur.

Cinq modules IoT sont enregistrés. `br-santos-01` et `br-rio-02` sont actifs au Brésil. `col-medellin-01` est actif en Colombie. `eq-quito-01` est inactif en Équateur. `br-santos-offline` est un module brésilien intentionnellement inactif depuis 45 minutes pour illustrer la détection de perte de connexion.

Quatre lots de café sont créés avec des statuts variés : `LOT-BR-001` est périmé (400 jours de stockage), `LOT-BR-002` est conforme (120 jours), `LOT-BR-003` est en alerte (60 jours, dans l'entrepôt de Rio qui a un capteur en anomalie), et `LOT-COL-001` est conforme en Colombie (15 jours).

Trois alertes actives pré-insérées correspondent à ces situations : une alerte de péremption sur `LOT-BR-001`, une alerte de conditionnement sur `br-rio-02` (surchauffe à 33.8°C pour un maximum admis de 32°C), et une alerte de perte de connexion sur `br-santos-offline`.

---

## 18. Sécurité — Considérations importantes

Le système de hachage des mots de passe utilise **SHA-256 avec un sel statique** (`futurekawa_secret_salt_123!`) codé en dur dans `app/utils/security.py`. Cette approche est fonctionnellement correcte pour un prototype mais insuffisante pour une production : le sel devrait être unique par utilisateur et un algorithme comme bcrypt ou Argon2 devrait être utilisé à la place.

Il n'y a pas de système de tokens JWT ou de sessions serveur. L'état d'authentification est entièrement géré dans le `localStorage` du navigateur côté client. Les endpoints de l'API backend ne sont protégés par aucun middleware d'authentification — toutes les routes sont accessibles sans token. Cela signifie que l'API est ouverte si elle est accessible depuis le réseau.

Le CORS est configuré pour n'autoriser que `http://localhost:3000`, ce qui restreint les appels cross-origin en développement.

Le broker Mosquitto est configuré avec `allow_anonymous true`, permettant à n'importe quel client de publier sur le topic IoT sans authentification.

---

## 19. Tests

### Backend
Les tests Python se trouvent dans `FutureKawaBresil_API/tests/`. Trois fichiers de tests sont présents. `test_security.py` vérifie les fonctions de hachage et de vérification des mots de passe. `test_schemas.py` teste la validation des schémas Pydantic (entrées valides et invalides). `test_lot_logic.py` teste les règles métier liées aux lots.

Pour exécuter les tests localement depuis le répertoire `FutureKawaBresil_API/` :
```bash
pip install pytest
pytest tests/ -v
```

### Frontend
Les tests TypeScript se trouvent dans `FutureKawa_Frontend/tests/`. Trois fichiers couvrent les composants de base. `gateway.test.ts` teste la logique du gateway multi-pays. `dialog.test.ts` teste le composant `UiDialog`. `pagination.test.ts` teste le composant `UiPagination`.

Pour exécuter les tests localement depuis le répertoire `FutureKawa_Frontend/` :
```bash
npm run test
```

---

## 20. Makefile

Un fichier `Makefile` à la racine du projet centralise les commandes courantes. Bien que son contenu ne soit pas reproduit ici, il s'utilise via la commande `make <cible>` depuis la racine du projet et constitue la façon la plus simple de lancer les opérations récurrentes de développement.

---

*Documentation générée sur la base de l'analyse du code source du dépôt `D:/FutureKawa/FutureKawa` en date du 19/06/2026.*

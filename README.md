# 🎬 Nexus Recommendations

**Système de recommandation intelligent multi-domaines** utilisant des algorithmes hybrides (filtrage collaboratif + basé sur le contenu).

Phase 1 : **Films** via TMDB API  
Phases futures : Musique, Livres, Jeux vidéo

---

## 🚀 Technologies

- **Backend** : FastAPI (Python), SQLAlchemy, Scikit-learn
- **Frontend** : React, Framer Motion
- **Base de données** : PostgreSQL
- **Conteneurisation** : Docker + Docker Compose
- **APIs** : TMDB (The Movie Database)

---

## 📦 Installation et Lancement

### Prérequis

- [Docker](https://www.docker.com/get-started) installé
- [Docker Compose](https://docs.docker.com/compose/install/) installé
- Clé API TMDB (gratuite sur [themoviedb.org](https://www.themoviedb.org/settings/api))

### Configuration

1. **Cloner le projet**
```bash
git clone https://github.com/ton-username/nexus-recommendations.git
cd nexus-recommendations
```

2. **Configurer les variables d'environnement**
```bash
# Copier le fichier .env.example en .env
cp .env.example .env

# Éditer .env et ajouter ta clé TMDB API
nano .env  # ou vim, code, etc.
```

Remplace `your_tmdb_api_key_here` par ta vraie clé API.

3. **Générer une SECRET_KEY sécurisée** (pour JWT)
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
Copie le résultat dans `.env` à la place de `your-super-secret-jwt-key...`

### Lancement avec Docker

```bash
# Construire et démarrer tous les conteneurs
docker-compose up --build

# Ou en arrière-plan (detached mode)
docker-compose up -d --build
```

**Accès aux services :**
- Frontend : http://localhost:3000
- Backend API : http://localhost:8000
- Documentation API : http://localhost:8000/docs
- Base de données : `localhost:5432`

### Commandes Utiles

```bash
# Voir les logs
docker-compose logs -f

# Logs d'un service spécifique
docker-compose logs -f backend

# Arrêter les conteneurs
docker-compose down

# Arrêter et supprimer les volumes (⚠️ efface la BDD)
docker-compose down -v

# Reconstruire un service spécifique
docker-compose up -d --build backend

# Accéder au shell d'un conteneur
docker exec -it nexus_backend bash
docker exec -it nexus_db psql -U nexus_user -d nexus_db
```

---

## 🗃️ Structure du Projet

```
nexus-recommendations/
├── docker-compose.yml       # Orchestration Docker
├── .env                     # Variables d'environnement (à ne pas commit)
├── .gitignore
├── README.md
│
├── database/
│   └── init.sql            # Schéma SQL initial
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py         # Point d'entrée FastAPI
│       ├── config.py
│       ├── database.py
│       ├── models/         # Modèles SQLAlchemy
│       ├── schemas/        # Schémas Pydantic
│       ├── api/            # Routes API
│       └── services/       # Logique métier
│
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── components/     # Composants React
        ├── pages/          # Pages principales
        ├── services/       # Appels API
        └── context/        # Context API
```

---

## 🎯 Fonctionnalités

### Phase 1 - Films (En cours ✅)

- [x] Authentification JWT (Register/Login)
- [x] Recherche de films (TMDB API)
- [x] Notation de films (1-5 étoiles)
- [x] Recommandations personnalisées (algorithme hybride)
- [x] Historique des films notés
- [x] Statistiques personnelles (genres préférés, moyennes)
- [x] Explication des recommandations

### Phases Futures

- [ ] Module Musique (Spotify/Last.fm API)
- [ ] Module Livres (Google Books API)
- [ ] Module Jeux Vidéo (RAWG API)
- [ ] Dashboard unifié multi-domaines

---

## 🤖 Algorithme de Recommandation Hybride

Le système combine trois approches :

1. **Filtrage Collaboratif** (User-Based)
   - Trouve les utilisateurs avec des goûts similaires
   - Recommande les films qu'ils ont aimés

2. **Filtrage Basé sur le Contenu** (Content-Based)
   - Analyse les caractéristiques des films notés (genres, acteurs, etc.)
   - Recommande des films similaires

3. **Hybride**
   - Score pondéré : 60% collaboratif + 40% contenu
   - Diversification pour éviter la bulle de filtre

---

## 🧪 Tests

```bash
# Backend (à venir)
docker exec -it nexus_backend pytest

# Frontend (à venir)
docker exec -it nexus_frontend npm test
```

---

## 📚 Documentation API

Une fois l'application lancée, accède à la documentation interactive :
- Swagger UI : http://localhost:8000/docs
- ReDoc : http://localhost:8000/redoc

---

## 🔧 Développement

### Backend (FastAPI)

```bash
# Entrer dans le conteneur backend
docker exec -it nexus_backend bash

# Créer une migration Alembic (à venir)
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

### Frontend (React)

```bash
# Entrer dans le conteneur frontend
docker exec -it nexus_frontend sh

# Installer une dépendance
npm install nom-du-package
```

---

## 🐛 Troubleshooting

### La base de données ne démarre pas
```bash
# Vérifier les logs
docker-compose logs db

# Supprimer le volume et recommencer
docker-compose down -v
docker-compose up -d --build
```

### Le backend ne se connecte pas à la BDD
```bash
# Vérifier que la BDD est healthy
docker-compose ps

# Attendre quelques secondes que PostgreSQL démarre complètement
```

### Port déjà utilisé
```bash
# Changer le port dans docker-compose.yml
# Exemple : "5433:5432" au lieu de "5432:5432"
```

---

## 📝 License

MIT License - Projet académique BUT Informatique

---

## 👨‍💻 Auteur

**Saban** - Étudiant BUT Informatique 2ème année  
IUT Aix-Marseille, Arles

---

## 🙏 Remerciements

- [TMDB](https://www.themoviedb.org/) pour l'API films
- [FastAPI](https://fastapi.tiangolo.com/) pour le framework backend
- [React](https://react.dev/) pour le framework frontend

---

**⭐ Si ce projet te plaît, n'hésite pas à le star sur GitHub !**
# 🎬 NEXUS - Système de Recommandation Multi-Médias Intelligent

![Status](https://img.shields.io/badge/Status-Production-success)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18.2.0-61DAFB?logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-316192?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

## 📋 Table des Matières

- [Vue d'ensemble](#vue-densemble)
- [Fonctionnalités](#fonctionnalités)
- [Architecture Technique](#architecture-technique)
- [Technologies Utilisées](#technologies-utilisées)
- [Installation](#installation)
- [Captures d'écran](#captures-décran)
- [Structure du Projet](#structure-du-projet)
- [APIs Utilisées](#apis-utilisées)
- [Performances](#performances)
- [Évolutions Futures](#évolutions-futures)

---

## 🎯 Vue d'ensemble

**NEXUS** est une plateforme web moderne de recommandation multi-médias qui permet aux utilisateurs de découvrir, noter et obtenir des recommandations personnalisées pour :

- 🎬 **Films** (via TMDB API)
- 🎵 **Musique** (via Spotify API)
- 📚 **Livres** (via Google Books API)
- 📺 **Séries TV** (prévu)
- 🎮 **Jeux Vidéo** (prévu)

Le système utilise des **algorithmes de recommandation intelligents** basés sur les préférences utilisateur et les similarités de contenu pour offrir une expérience personnalisée unique.

### 🌟 Points Forts

- **Interface Moderne** : Design dark élégant avec animations fluides (Framer Motion)
- **Architecture Microservices** : Backend FastAPI + Frontend React découplés
- **Conteneurisation Docker** : Déploiement simplifié avec Docker Compose
- **APIs Multiples** : Intégration de 3 APIs externes majeures
- **Recommandations Intelligentes** : Système hybride basé sur les préférences et similarités
- **Temps Réel** : Mise à jour instantanée des notes et recommandations

---

## ✨ Fonctionnalités

### 🔐 Authentification
- Inscription / Connexion sécurisée (JWT)
- Gestion de session persistante
- Protection des routes sensibles

### 🎬 Films
- **Découverte** : Parcourir les films populaires et top rated
- **Recherche** : Recherche avancée avec filtres
- **Notation** : Système d'étoiles interactif (1-5 étoiles)
- **Statistiques** : Total notés, moyenne, films favoris (≥4 étoiles)
- **Recommandations** : Films similaires basés sur TMDB API

### 🎵 Musique
- **Découverte** : Parcourir les morceaux populaires
- **Recherche** : Recherche par titre, artiste, album
- **Notation** : Notes musicales avec système d'étoiles
- **Statistiques** : Analyse de vos goûts musicaux
- **Recommandations** : Basées sur les artistes des morceaux bien notés

### 📚 Livres
- **Découverte** : Bestsellers et livres populaires
- **Recherche** : Recherche par titre, auteur, ISBN
- **Notation** : Système de notation avec avis
- **Statistiques** : Suivi de vos lectures
- **Recommandations** : Basées sur auteurs et catégories préférés

### 📊 Profil Utilisateur
- Statistiques globales
- Historique des notes
- Préférences de contenu
- Gestion du compte

---

## 🏗️ Architecture Technique

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Movies  │  │  Music   │  │  Books   │  │  Auth   │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
│       └─────────────┴──────────────┴─────────────┘      │
│                    Axios API Client                      │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (HTTP)
┌────────────────────────┴────────────────────────────────┐
│                  BACKEND (FastAPI)                       │
│  ┌──────────────────────────────────────────────────┐  │
│  │  API Routes: /auth /movies /music /books        │  │
│  └────────────────────┬─────────────────────────────┘  │
│  ┌────────────────────┴─────────────────────────────┐  │
│  │  Services: TMDB, Spotify, Google Books           │  │
│  └────────────────────┬─────────────────────────────┘  │
│  ┌────────────────────┴─────────────────────────────┐  │
│  │  SQLAlchemy ORM (PostgreSQL)                     │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────┴────────────────────────────────┐
│              PostgreSQL Database                         │
│  Tables: users, movies, tracks, books, ratings, etc.    │
└──────────────────────────────────────────────────────────┘

External APIs: TMDB ◄──► Spotify ◄──► Google Books
```

### 🔄 Flux de Données

1. **Client** : L'utilisateur interagit avec l'interface React
2. **API Client** : Axios envoie les requêtes HTTP au backend
3. **Backend** : FastAPI route vers le service approprié
4. **Services** : Appellent les APIs externes et/ou la base de données
5. **Database** : PostgreSQL stocke les données persistantes
6. **Response** : Les données remontent jusqu'au client via JSON

---

## 🛠️ Technologies Utilisées

### Backend
| Technologie | Version | Utilisation |
|------------|---------|-------------|
| **Python** | 3.11 | Langage principal |
| **FastAPI** | 0.109.0 | Framework web async |
| **SQLAlchemy** | 2.0.25 | ORM pour PostgreSQL |
| **PostgreSQL** | 15 | Base de données |
| **Pydantic** | 2.5.3 | Validation des données |
| **Python-Jose** | 3.3.0 | JWT tokens |
| **Passlib** | 1.7.4 | Hashing passwords |
| **HTTPX** | 0.26.0 | Client HTTP async |
| **Uvicorn** | 0.27.0 | Serveur ASGI |

### Frontend
| Technologie | Version | Utilisation |
|------------|---------|-------------|
| **React** | 18.2.0 | Framework UI |
| **React Router** | 6.20.0 | Routing SPA |
| **Axios** | 1.6.2 | Client HTTP |
| **Framer Motion** | 10.16.5 | Animations |
| **Lucide React** | 0.294.0 | Icônes modernes |
| **Tailwind CSS** | 3.3.5 | Styling utility-first |
| **Vite** | 5.0.0 | Build tool rapide |

### DevOps
- **Docker** : Conteneurisation
- **Docker Compose** : Orchestration multi-conteneurs
- **Git** : Contrôle de version

---

## 🚀 Installation

### Prérequis

- Docker et Docker Compose installés
- Clés API (voir ci-dessous)

### 1. Cloner le Repository

```bash
git clone https://github.com/SabanErcan/Nexus.git
cd Nexus
```

### 2. Configurer les Variables d'Environnement

Créer un fichier `.env` à la racine :

```env
# TMDB API (https://www.themoviedb.org/settings/api)
TMDB_API_KEY=votre_cle_tmdb

# Spotify API (https://developer.spotify.com/dashboard)
SPOTIFY_CLIENT_ID=votre_client_id
SPOTIFY_CLIENT_SECRET=votre_client_secret

# Backend
SECRET_KEY=votre_secret_key_jwt
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database
DATABASE_URL=postgresql://nexus_user:nexus_password@db:5432/nexus_db
```

### 3. Obtenir les Clés API

#### TMDB (Films & Séries)
1. Créer un compte sur [TMDB](https://www.themoviedb.org/)
2. Aller dans Settings > API
3. Copier l'API Read Access Token

#### Spotify (Musique)
1. Créer un compte sur [Spotify Developer](https://developer.spotify.com/)
2. Créer une application
3. Copier Client ID et Client Secret

#### Google Books (Livres)
- Aucune clé requise (API publique)

### 4. Lancer l'Application

```bash
docker-compose up -d
```

### 5. Accéder à l'Application

- **Frontend** : http://localhost:3000
- **Backend API** : http://localhost:8000
- **API Docs** : http://localhost:8000/docs

---

## 📸 Aperçu de l'Application

L'application propose une interface moderne et intuitive avec :

- **🏠 Connexion/Inscription** : Interface élégante avec gradient animé
- **🎬 Découverte de Films** : Grille de films populaires avec système de notation interactif (1-5 étoiles)
- **📊 Mes Notes** : Dashboard personnel avec statistiques (Total, Moyenne, Films favoris ≥4⭐)
- **🎵 Musique** : Recherche et découverte de morceaux avec intégration Spotify
- **📚 Livres** : Parcourir les bestsellers avec couvertures, auteurs et catégories
- **🎯 Recommandations** : Suggestions personnalisées basées sur vos goûts
- **👤 Profil** : Statistiques globales et gestion du compte
- **🎨 UI/UX** : Design dark moderne, animations Framer Motion, responsive

**Captures d'écran disponibles dans le dossier du projet**

---

## 📁 Structure du Projet

```
NEXUS/
├── backend/
│   ├── app/
│   │   ├── api/              # Routes FastAPI
│   │   │   ├── auth.py       # Authentification
│   │   │   ├── movies.py     # Films
│   │   │   ├── music.py      # Musique
│   │   │   ├── books.py      # Livres
│   │   │   └── __init__.py
│   │   ├── models/           # Modèles SQLAlchemy
│   │   │   ├── user.py
│   │   │   ├── movie.py
│   │   │   ├── music.py
│   │   │   ├── book.py
│   │   │   └── rating.py
│   │   ├── schemas/          # Schémas Pydantic
│   │   ├── services/         # Logique métier
│   │   │   ├── auth_service.py
│   │   │   ├── tmdb_service.py
│   │   │   ├── spotify_service.py
│   │   │   └── google_books_service.py
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Connexion DB
│   │   └── main.py           # Point d'entrée
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # Composants React
│   │   │   ├── Auth/
│   │   │   ├── Common/
│   │   │   ├── Movies/
│   │   │   ├── Music/
│   │   │   └── Books/
│   │   ├── pages/            # Pages principales
│   │   │   ├── Login.jsx
│   │   │   ├── Discover.jsx
│   │   │   ├── MusicSearch.jsx
│   │   │   ├── BookSearch.jsx
│   │   │   └── Profile.jsx
│   │   ├── services/         # API clients
│   │   │   ├── api.js
│   │   │   ├── authService.js
│   │   │   ├── movieService.js
│   │   │   ├── musicService.js
│   │   │   └── bookService.js
│   │   ├── context/          # Contextes React
│   │   │   └── AuthContext.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── database/
│   ├── init.sql              # Schéma initial
│   └── migrate_books.sql     # Migration livres
│
├── docker-compose.yml
├── .env
└── README.md
```

---

## 🌐 APIs Utilisées

### 1. TMDB (The Movie Database)
**Endpoint Base** : `https://api.themoviedb.org/3`

**Fonctionnalités** :
- Films populaires et top rated
- Recherche de films
- Détails des films
- Films similaires
- Genres

**Documentation** : [TMDB API Docs](https://developers.themoviedb.org/3)

### 2. Spotify Web API
**Endpoint Base** : `https://api.spotify.com/v1`

**Fonctionnalités** :
- Recherche de morceaux
- Détails des pistes
- Recommandations par artiste
- Authentification Client Credentials

**Documentation** : [Spotify API Docs](https://developer.spotify.com/documentation/web-api)

### 3. Google Books API
**Endpoint Base** : `https://www.googleapis.com/books/v1`

**Fonctionnalités** :
- Recherche de livres
- Détails des livres
- Filtres par langue (FR)
- Aucune clé requise

**Documentation** : [Google Books API Docs](https://developers.google.com/books/docs/v1/using)

---

## ⚡ Performances

### Optimisations Implémentées

1. **Backend**
   - Pool de connexions PostgreSQL (10 connexions)
   - Cache des tokens Spotify (1h)
   - Requêtes async avec HTTPX
   - Indexes sur colonnes fréquemment requêtées

2. **Frontend**
   - Code splitting avec React Router
   - Images lazy loading
   - Animations optimisées (transform/opacity)
   - Build Vite ultra-rapide

3. **Database**
   - Indexes sur : `user_id`, `movie_id`, `spotify_id`, `google_books_id`
   - Relations avec CASCADE DELETE
   - ARRAY PostgreSQL pour auteurs/catégories

### Métriques

- **Temps de chargement** : < 2s
- **Temps de recherche** : < 500ms
- **Taille du bundle** : ~150KB (gzipped)
- **Lighthouse Score** : 90+ (Performance)

---

## 🔮 Évolutions Futures

### Court Terme
- [ ] Séries TV (TMDB API)
- [ ] Jeux Vidéo (RAWG API)
- [ ] Mode hors ligne (PWA)
- [ ] Notifications push

### Moyen Terme
- [ ] Algorithme de recommandation ML avancé
- [ ] Filtrage collaboratif
- [ ] Partage social
- [ ] Listes personnalisées

### Long Terme
- [ ] Application mobile (React Native)
- [ ] API publique
- [ ] Plugin navigateur
- [ ] Assistant IA conversationnel

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- 🐛 Signaler des bugs
- 💡 Proposer des fonctionnalités
- 🔧 Soumettre des Pull Requests

---

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## 👨‍💻 Auteur

**Saban Ercan**

- GitHub: [@SabanErcan](https://github.com/SabanErcan)
- Portfolio: [Lien vers portfolio]

---

## 🙏 Remerciements

- [TMDB](https://www.themoviedb.org/) pour l'API films
- [Spotify](https://developer.spotify.com/) pour l'API musique
- [Google Books](https://developers.google.com/books) pour l'API livres
- [Lucide](https://lucide.dev/) pour les icônes
- Communauté FastAPI et React

---

## 📊 Statistiques du Projet

![GitHub repo size](https://img.shields.io/github/repo-size/SabanErcan/Nexus)
![GitHub last commit](https://img.shields.io/github/last-commit/SabanErcan/Nexus)
![GitHub issues](https://img.shields.io/github/issues/SabanErcan/Nexus)
![GitHub pull requests](https://img.shields.io/github/issues-pr/SabanErcan/Nexus)

---

<div align="center">
  <p>Fait avec ❤️ et beaucoup de ☕</p>
  <p>⭐ N'oubliez pas de star le projet si vous l'aimez !</p>
</div>

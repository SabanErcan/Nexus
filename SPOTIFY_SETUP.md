# Configuration Spotify API pour Nexus

## 🎵 Pourquoi la musique ne fonctionne pas ?

L'erreur **503 Service Unavailable** pour la musique est due aux identifiants Spotify manquants dans le fichier `.env`.

## 📝 Étapes pour configurer Spotify

### 1. Créer un compte développeur Spotify

1. Aller sur https://developer.spotify.com/dashboard
2. Se connecter avec votre compte Spotify (ou créer un compte gratuit)
3. Accepter les conditions d'utilisation

### 2. Créer une application

1. Cliquer sur **"Create app"** (Créer une application)
2. Remplir les informations :
   - **App name** : `Nexus Recommendations` (ou autre nom)
   - **App description** : `Application de recommandations multi-médias`
   - **Redirect URIs** : `http://localhost:3000/callback` (obligatoire, même si non utilisé)
   - **Which API/SDKs are you planning to use?** : Cocher **Web API**
3. Accepter les conditions et cliquer sur **Save**

### 3. Récupérer les identifiants

1. Une fois l'application créée, vous serez redirigé vers le dashboard
2. Cliquer sur **Settings** (en haut à droite)
3. Vous verrez :
   - **Client ID** : Une longue chaîne de caractères (ex: `abc123def456...`)
   - **Client secret** : Cliquer sur **"Show client secret"** pour l'afficher

### 4. Configurer le backend

1. Ouvrir le fichier **`backend/.env`**
2. Remplacer les valeurs placeholder par vos identifiants :

```env
SPOTIFY_CLIENT_ID=votre_client_id_ici
SPOTIFY_CLIENT_SECRET=votre_client_secret_ici
```

**Exemple :**
```env
SPOTIFY_CLIENT_ID=abc123def456ghi789jkl012mno345pq
SPOTIFY_CLIENT_SECRET=xyz789uvw456rst123opq890lmn678ijk
```

### 5. Redémarrer le backend

```powershell
docker-compose restart backend
```

## ✅ Vérification

1. Ouvrir http://localhost:3000
2. Se connecter et aller sur **Musique**
3. Rechercher un artiste (ex: "Jul", "Daft Punk")
4. Vous devriez voir des résultats apparaître !

## 🔍 Dépannage

### Erreur 503 persiste ?

Vérifier les logs backend :
```powershell
docker-compose logs backend | Select-String -Pattern "Spotify"
```

### Vérifier que les variables sont chargées :

```powershell
docker-compose exec backend env | Select-String -Pattern "SPOTIFY"
```

Vous devriez voir :
```
SPOTIFY_CLIENT_ID=abc123...
SPOTIFY_CLIENT_SECRET=xyz789...
```

### Les identifiants ne sont pas valides ?

- Vérifier qu'il n'y a **pas d'espaces** avant/après les valeurs
- Vérifier que le client secret est bien visible (cliquer sur "Show client secret")
- Régénérer un nouveau client secret si nécessaire (dans Settings → View client secret → Rotate)

## 📚 Limites Spotify API (Free Tier)

- **Quota** : 1000 requêtes par jour (largement suffisant pour tests)
- **Rate limit** : 30 requêtes par seconde
- **Restriction** : Mode Quota (ne nécessite pas de compte Spotify Premium)

## 🔗 Ressources

- [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- [Documentation Spotify Web API](https://developer.spotify.com/documentation/web-api)
- [Getting Started Guide](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

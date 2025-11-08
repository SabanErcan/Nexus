FROM node:20-alpine

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances nécessaires
RUN apk add --no-cache python3 make g++

# Copier les fichiers package
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code
COPY . .

# Exposer le port Vite
EXPOSE 3000

# Installer les dépendances de développement et démarrer le serveur de développement
CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0 --port 3000"]
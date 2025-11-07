FROM node:20-alpine

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers package
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier le reste du code
COPY . .

# Exposer le port Vite
EXPOSE 3000

# Démarrer le serveur de développement
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
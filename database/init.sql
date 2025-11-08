-- Nexus Recommendations Database Schema
-- Version 1.0 - Movies Module

-- Extension pour UUID (optionnel, utile pour les tokens)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================
-- TABLE: users
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index pour recherches rapides
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);

-- ============================================
-- TABLE: movies
-- ============================================
CREATE TABLE movies (
    id INTEGER PRIMARY KEY,  -- ID de TMDB API
    title VARCHAR(500) NOT NULL,
    original_title VARCHAR(500),
    overview TEXT,
    release_date DATE,
    poster_path VARCHAR(255),
    backdrop_path VARCHAR(255),
    vote_average DECIMAL(3,1),
    vote_count INTEGER,
    popularity DECIMAL(10,3),
    original_language VARCHAR(10),
    runtime INTEGER,  -- Durée en minutes
    budget BIGINT,
    revenue BIGINT,
    status VARCHAR(50),  -- Released, Post Production, etc.
    tagline TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_movies_title ON movies(title);
CREATE INDEX idx_movies_release_date ON movies(release_date);
CREATE INDEX idx_movies_popularity ON movies(popularity DESC);
CREATE INDEX idx_movies_vote_average ON movies(vote_average DESC);

-- ============================================
-- TABLE: genres
-- ============================================
CREATE TABLE genres (
    id INTEGER PRIMARY KEY,  -- ID de TMDB API
    name VARCHAR(100) NOT NULL UNIQUE
);

-- ============================================
-- TABLE: movie_genres (relation many-to-many)
-- ============================================
CREATE TABLE movie_genres (
    movie_id INTEGER REFERENCES movies(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES genres(id) ON DELETE CASCADE,
    PRIMARY KEY (movie_id, genre_id)
);

CREATE INDEX idx_movie_genres_movie ON movie_genres(movie_id);
CREATE INDEX idx_movie_genres_genre ON movie_genres(genre_id);

-- ============================================
-- TABLE: ratings
-- ============================================
CREATE TABLE ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, movie_id)  -- Un utilisateur ne peut noter qu'une fois chaque film
);

CREATE INDEX idx_ratings_user ON ratings(user_id);
CREATE INDEX idx_ratings_movie ON ratings(movie_id);
CREATE INDEX idx_ratings_rating ON ratings(rating);
CREATE INDEX idx_ratings_user_rating ON ratings(user_id, rating);

-- ============================================
-- TABLE: recommendations
-- ============================================
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    movie_id INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    score DECIMAL(5,3) NOT NULL CHECK (score >= 0 AND score <= 1),  -- Score entre 0 et 1
    algorithm_type VARCHAR(50) NOT NULL,  -- 'collaborative', 'content_based', 'hybrid'
    explanation TEXT,  -- "Parce que vous avez aimé X, Y, Z"
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT FALSE,  -- L'utilisateur a-t-il vu cette recommandation ?
    is_dismissed BOOLEAN DEFAULT FALSE  -- L'utilisateur a-t-il rejeté cette recommandation ?
);

CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_movie ON recommendations(movie_id);
CREATE INDEX idx_recommendations_score ON recommendations(score DESC);
CREATE INDEX idx_recommendations_user_score ON recommendations(user_id, score DESC);

-- ============================================
-- TABLE: user_movie_preferences
-- ============================================
CREATE TABLE user_movie_preferences (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    favorite_genres JSONB,  -- {"Action": 15, "Drama": 10, "Comedy": 8, ...}
    average_rating DECIMAL(3,2),  -- Moyenne des notes données
    total_ratings INTEGER DEFAULT 0,
    highly_rated_count INTEGER DEFAULT 0,  -- Nombre de films notés 4-5
    last_rating_date TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_preferences_user ON user_movie_preferences(user_id);

-- ============================================
-- TABLE: user_similarity (pour filtrage collaboratif)
-- ============================================
CREATE TABLE user_similarity (
    id SERIAL PRIMARY KEY,
    user_id_1 INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    user_id_2 INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    similarity_score DECIMAL(5,3) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    common_ratings_count INTEGER NOT NULL,
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (user_id_1 < user_id_2),  -- Éviter les doublons (A-B et B-A)
    UNIQUE(user_id_1, user_id_2)
);

CREATE INDEX idx_user_similarity_user1 ON user_similarity(user_id_1, similarity_score DESC);
CREATE INDEX idx_user_similarity_user2 ON user_similarity(user_id_2, similarity_score DESC);

-- ============================================
-- TABLE: movie_similarity (pour filtrage basé sur le contenu)
-- ============================================
CREATE TABLE movie_similarity (
    id SERIAL PRIMARY KEY,
    movie_id_1 INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    movie_id_2 INTEGER NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    similarity_score DECIMAL(5,3) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CHECK (movie_id_1 < movie_id_2),
    UNIQUE(movie_id_1, movie_id_2)
);

CREATE INDEX idx_movie_similarity_movie1 ON movie_similarity(movie_id_1, similarity_score DESC);
CREATE INDEX idx_movie_similarity_movie2 ON movie_similarity(movie_id_2, similarity_score DESC);

-- ============================================
-- TRIGGERS pour mise à jour automatique
-- ============================================

-- Trigger pour mettre à jour updated_at dans users
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_movies_updated_at BEFORE UPDATE ON movies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_ratings_updated_at BEFORE UPDATE ON ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Trigger pour mettre à jour les préférences utilisateur après une note
CREATE OR REPLACE FUNCTION update_user_preferences_on_rating()
RETURNS TRIGGER AS $$
DECLARE
    user_avg DECIMAL(3,2);
    user_total INTEGER;
    user_high_rated INTEGER;
BEGIN
    -- Calculer les statistiques
    SELECT 
        AVG(rating)::DECIMAL(3,2),
        COUNT(*),
        COUNT(*) FILTER (WHERE rating >= 4)
    INTO user_avg, user_total, user_high_rated
    FROM ratings
    WHERE user_id = NEW.user_id;

    -- Insérer ou mettre à jour les préférences
    INSERT INTO user_movie_preferences (
        user_id, 
        average_rating, 
        total_ratings, 
        highly_rated_count,
        last_rating_date,
        last_updated
    )
    VALUES (
        NEW.user_id, 
        user_avg, 
        user_total, 
        user_high_rated,
        NEW.created_at,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (user_id) 
    DO UPDATE SET
        average_rating = user_avg,
        total_ratings = user_total,
        highly_rated_count = user_high_rated,
        last_rating_date = NEW.created_at,
        last_updated = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_preferences_after_rating
    AFTER INSERT OR UPDATE ON ratings
    FOR EACH ROW
    EXECUTE FUNCTION update_user_preferences_on_rating();

-- ============================================
-- FONCTIONS UTILES
-- ============================================

-- Fonction pour obtenir les genres préférés d'un utilisateur
CREATE OR REPLACE FUNCTION get_user_favorite_genres(p_user_id INTEGER)
RETURNS TABLE(genre_name VARCHAR, rating_count BIGINT, avg_rating DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        g.name,
        COUNT(r.id) as rating_count,
        AVG(r.rating)::DECIMAL(3,2) as avg_rating
    FROM ratings r
    JOIN movie_genres mg ON r.movie_id = mg.movie_id
    JOIN genres g ON mg.genre_id = g.id
    WHERE r.user_id = p_user_id
    GROUP BY g.name
    ORDER BY COUNT(r.id) DESC, AVG(r.rating) DESC;
END;
$$ LANGUAGE plpgsql;

-- Fonction pour nettoyer les vieilles recommandations
CREATE OR REPLACE FUNCTION clean_old_recommendations(days_old INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM recommendations
    WHERE created_at < CURRENT_TIMESTAMP - INTERVAL '1 day' * days_old
    AND is_viewed = FALSE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- DONNÉES INITIALES (genres TMDB)
-- ============================================

INSERT INTO genres (id, name) VALUES
    (28, 'Action'),
    (12, 'Adventure'),
    (16, 'Animation'),
    (35, 'Comedy'),
    (80, 'Crime'),
    (99, 'Documentary'),
    (18, 'Drama'),
    (10751, 'Family'),
    (14, 'Fantasy'),
    (36, 'History'),
    (27, 'Horror'),
    (10402, 'Music'),
    (9648, 'Mystery'),
    (10749, 'Romance'),
    (878, 'Science Fiction'),
    (10770, 'TV Movie'),
    (53, 'Thriller'),
    (10752, 'War'),
    (37, 'Western')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- VUES UTILES
-- ============================================

-- Vue pour avoir un aperçu complet des films avec leurs genres
CREATE OR REPLACE VIEW movie_details_view AS
SELECT 
    m.id,
    m.title,
    m.original_title,
    m.overview,
    m.release_date,
    m.poster_path,
    m.backdrop_path,
    m.vote_average,
    m.vote_count,
    m.popularity,
    m.runtime,
    ARRAY_AGG(g.name ORDER BY g.name) as genres,
    COUNT(r.id) as total_ratings,
    AVG(r.rating)::DECIMAL(3,2) as avg_user_rating
FROM movies m
LEFT JOIN movie_genres mg ON m.id = mg.movie_id
LEFT JOIN genres g ON mg.genre_id = g.id
LEFT JOIN ratings r ON m.id = r.movie_id
GROUP BY m.id;

-- Vue pour les statistiques utilisateur
CREATE OR REPLACE VIEW user_stats_view AS
SELECT 
    u.id,
    u.username,
    u.email,
    ump.total_ratings,
    ump.average_rating,
    ump.highly_rated_count,
    ump.favorite_genres,
    ump.last_rating_date,
    COUNT(rec.id) as pending_recommendations
FROM users u
LEFT JOIN user_movie_preferences ump ON u.id = ump.user_id
LEFT JOIN recommendations rec ON u.id = rec.user_id AND rec.is_viewed = FALSE
GROUP BY u.id, ump.total_ratings, ump.average_rating, 
         ump.highly_rated_count, ump.favorite_genres, ump.last_rating_date;

-- ============================================
-- TABLES MUSIQUE (Spotify)
-- ============================================

-- Table des pistes musicales
CREATE TABLE tracks (
    id SERIAL PRIMARY KEY,
    spotify_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    artist VARCHAR(500) NOT NULL,
    album VARCHAR(500),
    release_year INTEGER,
    preview_url VARCHAR(500),
    image_url VARCHAR(500),
    duration_ms BIGINT,
    popularity INTEGER,
    genres JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tracks_spotify_id ON tracks(spotify_id);
CREATE INDEX idx_tracks_title ON tracks(title);
CREATE INDEX idx_tracks_artist ON tracks(artist);
CREATE INDEX idx_tracks_popularity ON tracks(popularity DESC);

-- Table des notes musicales
CREATE TABLE music_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, track_id)
);

CREATE INDEX idx_music_ratings_user ON music_ratings(user_id);
CREATE INDEX idx_music_ratings_track ON music_ratings(track_id);
CREATE INDEX idx_music_ratings_rating ON music_ratings(rating);

-- Table des recommandations musicales
CREATE TABLE music_recommendations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    track_id INTEGER NOT NULL REFERENCES tracks(id) ON DELETE CASCADE,
    score DECIMAL(5,3) NOT NULL CHECK (score >= 0 AND score <= 1),
    algorithm_type VARCHAR(50) NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_viewed BOOLEAN DEFAULT FALSE,
    is_dismissed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_music_recommendations_user ON music_recommendations(user_id);
CREATE INDEX idx_music_recommendations_track ON music_recommendations(track_id);
CREATE INDEX idx_music_recommendations_score ON music_recommendations(score DESC);

-- Trigger pour mise à jour de tracks
CREATE TRIGGER update_tracks_updated_at BEFORE UPDATE ON tracks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_music_ratings_updated_at BEFORE UPDATE ON music_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- TABLES LIVRES (OpenLibrary / Google Books)
-- ============================================

CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    author VARCHAR(500) NOT NULL,
    publisher VARCHAR(300),
    published_date DATE,
    isbn VARCHAR(20),
    description TEXT,
    cover_url VARCHAR(500),
    page_count INTEGER,
    language VARCHAR(10),
    categories JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_external_id ON books(external_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_author ON books(author);

CREATE TABLE book_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

CREATE INDEX idx_book_ratings_user ON book_ratings(user_id);
CREATE INDEX idx_book_ratings_book ON book_ratings(book_id);

-- ============================================
-- TABLES SÉRIES TV (TMDB)
-- ============================================

CREATE TABLE tv_shows (
    id INTEGER PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    original_name VARCHAR(500),
    overview TEXT,
    first_air_date DATE,
    poster_path VARCHAR(255),
    backdrop_path VARCHAR(255),
    vote_average DECIMAL(3,1),
    vote_count INTEGER,
    popularity DECIMAL(10,3),
    original_language VARCHAR(10),
    number_of_seasons INTEGER,
    number_of_episodes INTEGER,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_tv_shows_name ON tv_shows(name);
CREATE INDEX idx_tv_shows_popularity ON tv_shows(popularity DESC);

CREATE TABLE tv_genres (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE tv_show_genres (
    tv_show_id INTEGER REFERENCES tv_shows(id) ON DELETE CASCADE,
    genre_id INTEGER REFERENCES tv_genres(id) ON DELETE CASCADE,
    PRIMARY KEY (tv_show_id, genre_id)
);

CREATE TABLE tv_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tv_show_id INTEGER NOT NULL REFERENCES tv_shows(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, tv_show_id)
);

CREATE INDEX idx_tv_ratings_user ON tv_ratings(user_id);
CREATE INDEX idx_tv_ratings_tv_show ON tv_ratings(tv_show_id);

-- Genres TV TMDB
INSERT INTO tv_genres (id, name) VALUES
    (10759, 'Action & Adventure'),
    (16, 'Animation'),
    (35, 'Comedy'),
    (80, 'Crime'),
    (99, 'Documentary'),
    (18, 'Drama'),
    (10751, 'Family'),
    (10762, 'Kids'),
    (9648, 'Mystery'),
    (10763, 'News'),
    (10764, 'Reality'),
    (10765, 'Sci-Fi & Fantasy'),
    (10766, 'Soap'),
    (10767, 'Talk'),
    (10768, 'War & Politics'),
    (37, 'Western')
ON CONFLICT (id) DO NOTHING;

-- ============================================
-- TABLES JEUX VIDÉO (IGDB/RAWG)
-- ============================================

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    description TEXT,
    release_date DATE,
    cover_url VARCHAR(500),
    background_url VARCHAR(500),
    rating DECIMAL(3,1),
    platforms JSONB DEFAULT '[]',
    genres JSONB DEFAULT '[]',
    developers JSONB DEFAULT '[]',
    publishers JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_games_external_id ON games(external_id);
CREATE INDEX idx_games_name ON games(name);

CREATE TABLE game_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    game_id INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, game_id)
);

CREATE INDEX idx_game_ratings_user ON game_ratings(user_id);
CREATE INDEX idx_game_ratings_game ON game_ratings(game_id);

-- Triggers pour toutes les nouvelles tables
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_ratings_updated_at BEFORE UPDATE ON book_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tv_shows_updated_at BEFORE UPDATE ON tv_shows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tv_ratings_updated_at BEFORE UPDATE ON tv_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_games_updated_at BEFORE UPDATE ON games
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_game_ratings_updated_at BEFORE UPDATE ON game_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Message de succès
DO $$
BEGIN
    RAISE NOTICE '✅ Nexus Recommendations Database initialized successfully!';
    RAISE NOTICE '📊 Tables created: users, movies, genres, ratings, recommendations';
    RAISE NOTICE '🎵 Music tables: tracks, music_ratings, music_recommendations';
    RAISE NOTICE '📚 Books tables: books, book_ratings';
    RAISE NOTICE '📺 TV Shows tables: tv_shows, tv_genres, tv_ratings';
    RAISE NOTICE '🎮 Games tables: games, game_ratings';
    RAISE NOTICE '🎬 Genres seeded with TMDB standard genres';
END $$;
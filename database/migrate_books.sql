-- Migration de la table books pour Google Books API

-- Supprime l'ancienne structure
DROP TABLE IF EXISTS book_ratings CASCADE;
DROP TABLE IF EXISTS books CASCADE;

-- Crée la nouvelle table books avec le bon schéma
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    google_books_id VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    authors TEXT[] DEFAULT '{}',  -- Array de strings
    description TEXT,
    publisher VARCHAR(300),
    published_date VARCHAR(50),  -- Peut être "2024", "2024-01", "2024-01-15"
    page_count INTEGER,
    categories TEXT[] DEFAULT '{}',  -- Array de strings
    image_url VARCHAR(500),
    language VARCHAR(10),
    isbn_13 VARCHAR(20),
    average_rating DECIMAL(3,2),
    ratings_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_google_books_id ON books(google_books_id);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_authors ON books USING GIN(authors);
CREATE INDEX idx_books_categories ON books USING GIN(categories);

-- Recrée la table book_ratings
CREATE TABLE book_ratings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

CREATE INDEX idx_book_ratings_user ON book_ratings(user_id);
CREATE INDEX idx_book_ratings_book ON book_ratings(book_id);
CREATE INDEX idx_book_ratings_rating ON book_ratings(rating);

-- Trigger pour mise à jour automatique
CREATE TRIGGER update_books_updated_at BEFORE UPDATE ON books
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_book_ratings_updated_at BEFORE UPDATE ON book_ratings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Message de succès
DO $$
BEGIN
    RAISE NOTICE '✅ Migration books terminée avec succès!';
    RAISE NOTICE '📚 Colonnes: google_books_id, title, authors[], categories[], etc.';
END $$;

CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    original_price NUMERIC(12, 2),
    current_price NUMERIC(12, 2) NOT NULL,
    discount_percent NUMERIC(5, 2),
    quantity INTEGER,
    category TEXT,
    n_review INTEGER,
    avg_rating NUMERIC(3, 2),
    pages INTEGER,
    manufacturer TEXT,
    cover_link TEXT
);

CREATE TABLE IF NOT EXISTS comments (
    comment_id BIGINT PRIMARY KEY,
    product_id BIGINT NOT NULL,
    customer_id BIGINT,
    rating INTEGER NOT NULL,
    title TEXT,
    thank_count INTEGER DEFAULT 0,
    content TEXT
);

CREATE INDEX IF NOT EXISTS idx_books_category ON books(category);
CREATE INDEX IF NOT EXISTS idx_books_authors ON books(authors);
CREATE INDEX IF NOT EXISTS idx_books_current_price ON books(current_price);
CREATE INDEX IF NOT EXISTS idx_comments_product_id ON comments(product_id);
CREATE INDEX IF NOT EXISTS idx_comments_rating ON comments(rating);
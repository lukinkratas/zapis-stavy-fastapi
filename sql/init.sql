-- CREATE TYPE public.userrole AS ENUM (
--     'READ_ONLY',
--     'STANDARD',
--     'ADMIN'
-- );

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    confirmed BOOLEAN NOT NULL DEFAULT FALSE
    -- role public.userrole NOT NULL DEFAULT 'STANDARD',
);

-- automatically created by the unique constraint
-- CREATE INDEX idx_users_email ON users(email);

-- INSERT INTO users (id, email, password)
-- VALUES (
--     'e49a1d7f-50fc-4095-9740-346b79f4711b',
--     'default@email.net',
--     '$argon2id$v=19$m=65536,t=3,p=4$pxJ6xPDuqKDjRPRwENjYMA$sgGd5fmjB/x7WIC4rZKsMl468DEJSrCYDeqsNxs3qAM'
-- );

-- SELECT * FROM users;

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    CONSTRAINT unique_location_name UNIQUE (user_id, name)
);

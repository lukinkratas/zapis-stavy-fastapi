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

CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuidv7(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    location_name TEXT NOT NULL,
    CONSTRAINT unique_location_name UNIQUE (user_id, location_name)
);

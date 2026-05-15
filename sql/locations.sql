CREATE TABLE locations (
    id UUID DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    PRIMARY KEY (id),
    CONSTRAINT unique_location_name UNIQUE (user_id, name)
);

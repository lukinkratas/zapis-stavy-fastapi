CREATE TABLE locations (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    CONSTRAINT unique_location_name UNIQUE (user_id, name),
    PRIMARY key (id)
);

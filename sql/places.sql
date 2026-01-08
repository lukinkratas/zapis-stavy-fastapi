CREATE TABLE places (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    address TEXT DEFAULT NULL,
    CONSTRAINT unique_place_name UNIQUE (name),
    PRIMARY key (id)
);

INSERT INTO places (name)
VALUES ('default');

-- SELECT * FROM places;

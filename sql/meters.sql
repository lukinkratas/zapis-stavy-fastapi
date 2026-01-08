CREATE TABLE meters (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    CONSTRAINT unique_meter_name UNIQUE (name),
    PRIMARY key (id)
);

INSERT INTO meters (id, name)
VALUES ('5ad4f210-cdfb-4196-82f7-af6afda013ea', 'default');

-- SELECT * FROM meters;

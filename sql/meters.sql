CREATE TABLE meters (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    CONSTRAINT unique_meter_name UNIQUE (name),
    PRIMARY key (id)
);

-- INSERT INTO meters (id, user_id, name)
-- VALUES ('5ad4f210-cdfb-4196-82f7-af6afda013ea', 'e49a1d7f-50fc-4095-9740-346b79f4711b', 'default');

-- SELECT * FROM meters;

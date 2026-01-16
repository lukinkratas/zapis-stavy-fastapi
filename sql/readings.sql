SET timezone = 'Europe/Prague';

CREATE TABLE readings (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    meter_id UUID NOT NULL REFERENCES meters(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    value DOUBLE PRECISION NOT NULL,
    PRIMARY key (id)
);

-- INSERT INTO readings (id, meter_id, value)
-- VALUES ('d09b982f-ffe7-42d1-809f-5c61eeac9f99', '5ad4f210-cdfb-4196-82f7-af6afda013ea', 11.0);

-- SELECT * FROM readings;

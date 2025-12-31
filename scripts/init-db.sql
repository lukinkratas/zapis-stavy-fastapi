-- DROP TABLE IF EXISTS public.meters;

CREATE TABLE public.meters (
    id UUID DEFAULT uuidv4(),
    name TEXT NOT NULL,
    description TEXT DEFAULT NULL,
    PRIMARY key (id)
);

-- SELECT * FROM public.meters;

-- CREATE TYPE public.userrole AS ENUM (
--     'STANDARD',
--     'PREMIUM',
--     'ADMIN'
-- );

-- -- ==========================
-- -- 1. USERS
-- -- ==========================
-- CREATE TABLE users (
--     id BIGSERIAL PRIMARY KEY,
--     email TEXT NOT NULL UNIQUE,
--     name TEXT NOT NULL,
--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
-- );

-- -- Index for common lookups
-- CREATE INDEX idx_users_email ON users(email);


-- -- ==========================
-- -- 2. UTILITY TYPES (user-defined)
-- -- ==========================
-- CREATE TABLE utility_types (
--     id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     name TEXT NOT NULL,                -- e.g. "electricity", "cold_water", "garage_heating"
--     unit TEXT DEFAULT NULL,            -- optional, e.g. "kWh", "m3", etc.
--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

--     -- Each user cannot create the same utility type name twice
--     CONSTRAINT unique_user_type_name UNIQUE (user_id, name)
-- );

-- CREATE INDEX idx_utility_types_user ON utility_types(user_id);


-- -- ==========================
-- -- 3. METERS (optional multiple sources per utility)
-- -- ==========================
-- CREATE TABLE meters (
--     id BIGSERIAL PRIMARY KEY,
--     user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
--     utility_type_id BIGINT NOT NULL REFERENCES utility_types(id) ON DELETE CASCADE,

--     name TEXT NOT NULL,                -- e.g. "Main meter", "Garage meter"
--     description TEXT DEFAULT NULL,

--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

--     -- Each user cannot have two meters with the same name for the same utility
--     CONSTRAINT unique_meter_name_per_type UNIQUE (user_id, utility_type_id, name)
-- );

-- CREATE INDEX idx_meters_user ON meters(user_id);
-- CREATE INDEX idx_meters_type ON meters(utility_type_id);


-- -- ==========================
-- -- 4. READINGS (time-series)
-- -- ==========================
-- CREATE TABLE readings (
--     id BIGSERIAL PRIMARY KEY,
--     meter_id BIGINT NOT NULL REFERENCES meters(id) ON DELETE CASCADE,

--     reading_at TIMESTAMPTZ NOT NULL,   -- timestamp of reading
--     value DOUBLE PRECISION NOT NULL,   -- consumption value

--     extra JSONB DEFAULT '{}'::jsonb,   -- optional flexible metadata
--     created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

--     -- No duplicate readings per meter at the exact timestamp
--     CONSTRAINT unique_meter_timestamp UNIQUE (meter_id, reading_at)
-- );

-- -- Index for time-series queries
-- CREATE INDEX idx_readings_meter_time ON readings(meter_id, reading_at);

-- -- Index for JSON operations (optional)
-- CREATE INDEX idx_readings_extra_gin ON readings USING GIN (extra);

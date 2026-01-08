CREATE TABLE users (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    CONSTRAINT unique_user_email UNIQUE (email),
    PRIMARY key (id)
);

INSERT INTO users (id, email, password)
VALUES ('e49a1d7f-50fc-4095-9740-346b79f4711b', 'default@email.net', 'xxx111');

-- SELECT * FROM users;

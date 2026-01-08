CREATE TABLE users (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    email TEXT NOT NULL,
    password TEXT NOT NULL,
    CONSTRAINT unique_email_name UNIQUE (name),
    PRIMARY key (id)
);

INSERT INTO meters (email, password)
VALUES ('root', 'pswd1234');

-- SELECT * FROM users;

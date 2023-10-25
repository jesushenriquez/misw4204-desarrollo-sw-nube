CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    source_uuid uuid NOT NULL,
    source_name varchar(1000),
    source_format varchar(5),
    target_format varchar(5),
    create_datetime timestamp,
    start_convert timestamp,
    end_convert timestamp,
    status varchar(20),
    user_id INT REFERENCES users(id)
);
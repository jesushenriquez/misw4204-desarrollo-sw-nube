CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    source_uuid _uuid NOT NULL,
    source_name varchar(1000),
    source_format varchar(5),
    target_format varchar(5),
    create_datetime timestamp,
    start_convert timestamp,
    end_convert timestamp,
    status varchar(20)
);

ALTER TABLE tasks
ADD COLUMN user_id INT REFERENCES users(id);
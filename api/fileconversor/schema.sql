DROP TABLE IF EXISTS employer_audit;

CREATE TABLE employer_audit (
    id SERIAL PRIMARY KEY,
    employer_username VARCHAR(255) NOT NULL,
    candidate VARCHAR(255) NOT NULL,
    data_extraction_date TIMESTAMP NOT NULL,
    creation_date TIMESTAMP NOT NULL
);
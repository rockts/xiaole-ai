-- v0.9.0 Phase 1: Create face_encodings table
CREATE TABLE IF NOT EXISTS face_encodings (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) DEFAULT 'default_user',
    name VARCHAR(100) NOT NULL,
    encoding FLOAT[],
    image_path VARCHAR(500),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT now()
);

CREATE INDEX IF NOT EXISTS ix_face_encodings_user_id ON face_encodings (user_id);

create database supernova;

use supernova;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    user_email VARCHAR(100) UNIQUE NOT NULL,
    user_password VARCHAR(255) NOT NULL,
    user_mobile VARCHAR(15),
    user_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE sst_tts (
    sst_tts_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    sst_url TEXT,
    sst_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sst_duration FLOAT,
    text_data_user TEXT,
    text_data_bot TEXT,
    tts_url TEXT,
    tts_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tts_duration FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

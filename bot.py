-- Статуси користувачів
CREATE TYPE user_status AS ENUM ('active', 'blocked', 'suspended');

-- Таблиця користувачів
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255),
    language VARCHAR(10) DEFAULT 'uk',
    status user_status DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Бухгалтерська система (Ledger) для всіх фінансових операцій
CREATE TABLE ledger_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    type VARCHAR(50) NOT NULL, -- DEPOSIT, BET, WIN, REFUND, WITHDRAWAL, etc.
    amount NUMERIC(18, 8) NOT NULL,
    currency VARCHAR(20) NOT NULL DEFAULT 'TON',
    balance_before NUMERIC(18, 8) NOT NULL,
    balance_after NUMERIC(18, 8) NOT NULL,
    reference_type VARCHAR(50), -- games, deposits, withdrawals
    reference_id INTEGER,
    status VARCHAR(30) DEFAULT 'completed',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Таблиця ігор
CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    status VARCHAR(30) DEFAULT 'active', -- created, active, won, lost, cashed_out
    bet_amount NUMERIC(18, 8) NOT NULL,
    currency VARCHAR(20) DEFAULT 'TON',
    grid_size INTEGER DEFAULT 36,
    bomb_count INTEGER DEFAULT 6,
    server_seed_hash VARCHAR(64) NOT NULL,
    server_seed VARCHAR(64),
    client_seed VARCHAR(64),
    nonce INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP WITH TIME ZONE
);

-- Ігрові ходи (відкриті комірки)
CREATE TABLE game_moves (
    id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES games(id),
    cell_index INTEGER NOT NULL,
    result VARCHAR(20) NOT NULL, -- star, bomb
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_game_cell UNIQUE (game_id, cell_index)
);

-- Депозити
CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount NUMERIC(18, 8) NOT NULL,
    currency VARCHAR(20) DEFAULT 'TON',
    tx_hash VARCHAR(128) UNIQUE NOT NULL,
    status VARCHAR(30) DEFAULT 'pending', -- pending, confirmed, credited, failed
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Виплати (Withdrawals)
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    amount NUMERIC(18, 8) NOT NULL,
    fee NUMERIC(18, 8) DEFAULT 0,
    net_amount NUMERIC(18, 8) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    currency VARCHAR(20) DEFAULT 'TON',
    status VARCHAR(30) DEFAULT 'requested', -- requested, approved, processing, completed, rejected
    tx_hash VARCHAR(128),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Аудит-лог
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER,
    action VARCHAR(100) NOT NULL,
    target_type VARCHAR(50),
    target_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

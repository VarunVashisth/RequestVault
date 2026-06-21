-- PostgreSQL Migration for AI Observability
-- File: app/migrations/001_add_ai_observability_up.sql

-- Create ai_requests table
CREATE TABLE IF NOT EXISTS ai_requests (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL UNIQUE,
    provider VARCHAR(50) NOT NULL,
    model VARCHAR(255) NOT NULL,
    input_tokens INTEGER,
    output_tokens INTEGER,
    total_tokens INTEGER,
    estimated_cost DOUBLE PRECISION,
    latency_ms INTEGER,
    usage_metadata JSONB,
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_request_id FOREIGN KEY (request_id) 
        REFERENCES requests(id) ON DELETE CASCADE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_ai_provider ON ai_requests(provider);
CREATE INDEX IF NOT EXISTS idx_ai_model ON ai_requests(model);
CREATE INDEX IF NOT EXISTS idx_ai_created_at ON ai_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_ai_request_id ON ai_requests(request_id);

-- Create ai_provider_configs table
CREATE TABLE IF NOT EXISTS ai_provider_configs (
    id SERIAL PRIMARY KEY,
    provider VARCHAR(50) NOT NULL UNIQUE,
    models JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT uk_provider UNIQUE (provider)
);

CREATE INDEX IF NOT EXISTS idx_config_provider ON ai_provider_configs(provider);

-- Insert default provider configurations
INSERT INTO ai_provider_configs (provider, models) VALUES
('openai', '{
  "gpt-4-turbo": {"input": 0.01, "output": 0.03},
  "gpt-4o": {"input": 0.005, "output": 0.015},
  "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
  "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
  "gpt-4": {"input": 0.03, "output": 0.06}
}')
ON CONFLICT (provider) DO NOTHING;

INSERT INTO ai_provider_configs (provider, models) VALUES
('anthropic', '{
  "claude-3-opus": {"input": 0.015, "output": 0.075, "cache_input": 0.00375},
  "claude-3-sonnet": {"input": 0.003, "output": 0.015, "cache_input": 0.00075},
  "claude-3-haiku": {"input": 0.00025, "output": 0.00125, "cache_input": 0.0000625},
  "claude-3-5-sonnet": {"input": 0.003, "output": 0.015, "cache_input": 0.00075},
  "claude-3-5-haiku": {"input": 0.00025, "output": 0.00125, "cache_input": 0.0000625}
}')
ON CONFLICT (provider) DO NOTHING;

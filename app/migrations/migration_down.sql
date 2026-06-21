

-- Drop indexes
DROP INDEX IF EXISTS idx_ai_provider;
DROP INDEX IF EXISTS idx_ai_model;
DROP INDEX IF EXISTS idx_ai_created_at;
DROP INDEX IF EXISTS idx_ai_request_id;
DROP INDEX IF EXISTS idx_config_provider;

-- Drop tables
DROP TABLE IF EXISTS ai_requests CASCADE;
DROP TABLE IF EXISTS ai_provider_configs CASCADE;

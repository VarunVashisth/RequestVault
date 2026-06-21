"""
Database Migration Script
File: app/migrations/add_ai_observability.py

Creates the ai_requests and ai_provider_configs tables.
Run this BEFORE deploying the AI observability feature.

Usage:
    python -m alembic upgrade head
    
Or manually with SQL:
    psql -d requestvault -f migration_up.sql
    sqlite3 requestvault.db < migration_up.sql
"""

from sqlalchemy import create_engine, text
import logging

logger = logging.getLogger(__name__)


def migrate_up(db_url: str):
    """Create AI observability tables."""
    
    engine = create_engine(db_url)
    
    sql = """
    -- Create ai_requests table
    CREATE TABLE IF NOT EXISTS ai_requests (
        id SERIAL PRIMARY KEY,
        request_id INTEGER NOT NULL UNIQUE,
        provider VARCHAR(50) NOT NULL,
        model VARCHAR(255) NOT NULL,
        input_tokens INTEGER,
        output_tokens INTEGER,
        total_tokens INTEGER,
        estimated_cost FLOAT,
        latency_ms INTEGER,
        usage_metadata JSON,
        tags JSON,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        
        FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
        INDEX idx_provider (provider),
        INDEX idx_model (model),
        INDEX idx_created_at (created_at)
    );

    -- Create ai_provider_configs table
    CREATE TABLE IF NOT EXISTS ai_provider_configs (
        id SERIAL PRIMARY KEY,
        provider VARCHAR(50) NOT NULL UNIQUE,
        models JSON NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        
        INDEX idx_provider (provider)
    );
    """
    
    try:
        with engine.connect() as conn:
            # Split and execute each statement
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        
        logger.info("Migration completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False


def migrate_down(db_url: str):
    """Drop AI observability tables."""
    
    engine = create_engine(db_url)
    
    sql = """
    DROP TABLE IF EXISTS ai_requests CASCADE;
    DROP TABLE IF EXISTS ai_provider_configs CASCADE;
    """
    
    try:
        with engine.connect() as conn:
            for statement in sql.split(';'):
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        
        logger.info("Rollback completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Rollback failed: {e}")
        return False


# For PostgreSQL with Alembic
def alembic_upgrade(op):
    """Alembic upgrade function."""
    
    op.create_table(
        'ai_requests',
        with_columns=[
            op.Column('id', op.Integer(), nullable=False),
            op.Column('request_id', op.Integer(), nullable=False),
            op.Column('provider', op.String(length=50), nullable=False),
            op.Column('model', op.String(length=255), nullable=False),
            op.Column('input_tokens', op.Integer(), nullable=True),
            op.Column('output_tokens', op.Integer(), nullable=True),
            op.Column('total_tokens', op.Integer(), nullable=True),
            op.Column('estimated_cost', op.Float(), nullable=True),
            op.Column('latency_ms', op.Integer(), nullable=True),
            op.Column('usage_metadata', op.JSON(), nullable=True),
            op.Column('tags', op.JSON(), nullable=True),
            op.Column('created_at', op.DateTime(timezone=True), server_default='CURRENT_TIMESTAMP'),
            op.PrimaryKeyConstraint('id'),
            op.ForeignKeyConstraint(['request_id'], ['requests.id'], ondelete='CASCADE'),
        ]
    )
    
    op.create_index('idx_ai_provider', 'ai_requests', ['provider'])
    op.create_index('idx_ai_model', 'ai_requests', ['model'])
    op.create_index('idx_ai_created_at', 'ai_requests', ['created_at'])
    
    op.create_table(
        'ai_provider_configs',
        [
            op.Column('id', op.Integer(), nullable=False),
            op.Column('provider', op.String(length=50), nullable=False),
            op.Column('models', op.JSON(), nullable=False),
            op.Column('updated_at', op.DateTime(timezone=True), server_default='CURRENT_TIMESTAMP'),
            op.PrimaryKeyConstraint('id'),
            op.UniqueConstraint('provider'),
        ]
    )
    
    op.create_index('idx_config_provider', 'ai_provider_configs', ['provider'])


def alembic_downgrade(op):
    """Alembic downgrade function."""
    
    op.drop_table('ai_requests')
    op.drop_table('ai_provider_configs')

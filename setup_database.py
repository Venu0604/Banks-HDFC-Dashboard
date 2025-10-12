"""
Database Setup Script
Creates necessary tables for MIS update tracking
"""

from sqlalchemy import create_engine, text


def setup_database():
    """Create MIS_Update_Log table if it doesn't exist"""

    # Database connection
    engine = create_engine("postgresql+psycopg2://postgres:1234@localhost:5432/Nxtify")

    # SQL to create MIS_Update_Log table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS "MIS_Update_Log" (
        id SERIAL PRIMARY KEY,
        table_name VARCHAR(255) NOT NULL,
        record_count INTEGER NOT NULL,
        updated_at TIMESTAMP NOT NULL,
        updated_by VARCHAR(255),
        notes TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_mis_update_log_table
    ON "MIS_Update_Log" (table_name, updated_at DESC);
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
        print("✅ Database setup completed successfully!")
        print("✅ MIS_Update_Log table created/verified")
        return True
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Setting up database...")
    setup_database()

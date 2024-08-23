from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base # Ensure Base is imported from models

# Setup the engine
engine = create_engine(
    'mysql+pymysql://root:12345@localhost/fastapidemo',
    echo=True
)

# Create all tables
Base.metadata.create_all(bind=engine)

# Setup the session
SessionLocal = sessionmaker(bind=engine)

# Verify table creation
inspector = inspect(engine)
tables = inspector.get_table_names()
print("Tables in the database:", tables)

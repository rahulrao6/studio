
from typing import Generator
from sqlalchemy.orm import Session
from core.database import SessionLocal

def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Usage:
        @app.get("/items/")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
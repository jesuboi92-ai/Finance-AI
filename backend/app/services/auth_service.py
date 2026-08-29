from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password
from datetime import datetime

class AuthService:
    def create_user(self, db: Session, user: UserCreate) -> User:
        """Create new user with hashed password"""
        hashed_password = hash_password(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password,
            role=user.role,
            department=user.department,
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, db: Session, email: str, password: str) -> User:
        """Authenticate user by email and password"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        
        user.last_login = datetime.utcnow()
        db.commit()
        return user
    
    def verify_refresh_token(self, token: str) -> str:
        """Verify refresh token and return user_id"""
        # Implementation would verify JWT token
        try:
            from app.utils.security import decode_token
            payload = decode_token(token)
            return payload.get("sub")
        except:
            return None

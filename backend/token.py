from datetime import datetime, timedelta
from jose import JWTError, jwt

from configuration import JWT_CONFIG

SECRET_KEY = JWT_CONFIG.SECRET_KEY
ALGORITHM = JWT_CONFIG.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = JWT_CONFIG.ACCESS_TOKEN_EXPIRE_MINUTES


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return False
        
        return email
    
    except JWTError as e:
        print(f"Token verification failed: {e}")
        return False
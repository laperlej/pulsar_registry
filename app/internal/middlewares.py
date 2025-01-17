from fastapi import Depends
from .config import AppConfig
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def token_verification(config: AppConfig):
    bearer_token = config.auth.bearer_token
    
    async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
        if bearer_token is None:
            return None
            
        if credentials.credentials != bearer_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return None
        
    return verify_token

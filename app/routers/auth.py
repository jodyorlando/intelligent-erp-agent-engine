from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.limiter import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Mock database user for development
MOCK_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": get_password_hash("admin123"),
        "role": "admin"
    }
}

@router.post("/login")
@limiter.limit("5/minute")
async def login_access_token(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user credentials and return a signed JWT token.
    Rate limited to 5 attempts per minute per IP.
    """
    user = MOCK_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}
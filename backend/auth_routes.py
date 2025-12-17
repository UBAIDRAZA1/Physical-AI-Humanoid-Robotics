"""
Authentication routes: Signup, Login, Profile, and protected endpoints.
Professional implementation compatible with BetterAuth patterns.
"""
from typing import Optional
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from starlette.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from database import get_db, User
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_user_from_token,
    generate_user_id,
)
from oauth import oauth, is_google_oauth_enabled

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()

# Request/Response Models
class SignupRequest(BaseModel):
    email: EmailStr
    name: str
    password: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    software_background: Optional[str] = None
    hardware_background: Optional[str] = None
    email_verified: bool
    created_at: str
    image: Optional[str] = None
    role: str

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# Dependency to get current user (required)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    Raises 401 if token is missing or invalid.
    """
    token = credentials.credentials
    user_data = get_user_from_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_data["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user


# Optional dependency for routes that work with or without auth
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
) -> Optional[User]:
    """
    Optional dependency to get current user if token is provided.
    Returns None if no token, invalid token, or database not configured (doesn't raise error).
    """
    if not credentials:
        return None
    
    try:
        # Check if database is configured
        from database import DATABASE_URL, SessionLocal
        if not DATABASE_URL or not SessionLocal:
            return None
        
        token = credentials.credentials
        user_data = get_user_from_token(token)
        
        if not user_data:
            return None
        
        # Get database session
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_data["user_id"]).first()
            return user
        finally:
            db.close()
    except Exception as e:
        # If any error occurs, just return None (optional auth)
        print(f"Optional auth error (ignored): {e}")
        return None


# Routes
@router.get("/login/google")
async def login_google(request: Request):
    """
    Redirect to Google for authentication.
    """
    if not await is_google_oauth_enabled():
        raise HTTPException(status_code=404, detail="Google OAuth is not configured")
    
    redirect_uri = request.url_for('auth_google')
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google", response_model=AuthResponse)
async def auth_google(request: Request, db: Session = Depends(get_db)):
    """
    Google OAuth2 callback endpoint.
    Handles user creation and login after Google authentication.
    """
    if not await is_google_oauth_enabled():
        raise HTTPException(status_code=404, detail="Google OAuth is not configured")

    try:
        token = await oauth.google.authorize_access_token(request)
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Google login failed: {e}")

    user_info = token.get('userinfo')
    if not user_info:
        raise HTTPException(status_code=400, detail="Could not retrieve user info from Google")

    email = user_info.get('email')
    if not email:
        raise HTTPException(status_code=400, detail="No email found in Google account")

    # Check if user already exists
    user = db.query(User).filter(User.email == email).first()

    if not user:
        # Create new user if they don't exist
        user_id = generate_user_id()
        new_user = User(
            id=user_id,
            email=email,
            name=user_info.get('name', 'New User'),
            image=user_info.get('picture'),
            email_verified=user_info.get('email_verified', False),
            password_hash=None,  # No password for OAuth users
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user
    elif not user.image and user_info.get('picture'):
        # Update image if it's missing
        user.image = user_info.get('picture')
        db.commit()
        db.refresh(user)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.from_orm(user),
    )


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """
    User registration endpoint.
    Creates a new user with email, password, and optional background fields.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Validate password strength
    if len(request.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long",
        )
    
    # Create new user
    user_id = generate_user_id()
    hashed_password = hash_password(request.password)
    
    new_user = User(
        id=user_id,
        email=request.email,
        name=request.name,
        password_hash=hashed_password,
        software_background=request.software_background,
        hardware_background=request.hardware_background,
        email_verified=False,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_id, "email": request.email}
    )
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse.from_orm(new_user),
    )



@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    User login endpoint.
    Authenticates user and returns JWT token.
    """
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return AuthResponse(
        access_token=access_token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            name=user.name,
            software_background=user.software_background,
            hardware_background=user.hardware_background,
            email_verified=user.email_verified,
            created_at=user.created_at.isoformat(),
            image=user.image,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's profile.
    Protected route - requires valid JWT token.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        software_background=current_user.software_background,
        hardware_background=current_user.hardware_background,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at.isoformat(),
        image=current_user.image,
        role=current_user.role,
    )


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    name: Optional[str] = None,
    software_background: Optional[str] = None,
    hardware_background: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.
    Protected route - requires valid JWT token.
    """
    if request.name is not None:
        current_user.name = request.name
    if request.software_background is not None:
        current_user.software_background = request.software_background
    if request.hardware_background is not None:
        current_user.hardware_background = request.hardware_background
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        software_background=current_user.software_background,
        hardware_background=current_user.hardware_background,
        email_verified=current_user.email_verified,
        created_at=current_user.created_at.isoformat(),
        image=current_user.image,
        role=current_user.role,
    )


@router.post("/verify-token", response_model=UserResponse)
async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Verify if a JWT token is valid and return user information.
    """
    token = credentials.credentials
    user_data = get_user_from_token(token)
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user = db.query(User).filter(User.id == user_data["user_id"]).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        software_background=user.software_background,
        hardware_background=user.hardware_background,
        email_verified=user.email_verified,
        created_at=user.created_at.isoformat(),
        image=user.image,
        role=user.role,
    )


# Authentication System Documentation

Professional JWT-based authentication system compatible with BetterAuth patterns.

## Features

✅ **JWT Token Authentication**
- Secure token generation and verification
- 7-day token expiration
- Bearer token authentication

✅ **User Management**
- Signup with email/password
- Login with credentials
- Profile management
- Custom fields for personalization:
  - `software_background`: User's software experience
  - `hardware_background`: User's hardware experience

✅ **Security**
- Password hashing with bcrypt
- JWT secret key from environment
- Password strength validation (min 8 characters)
- Protected routes with authentication middleware

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Add to `.env` file:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host/dbname

# JWT Secret (generate a secure random string)
JWT_SECRET_KEY=your-secret-key-here-min-32-chars
```

### 3. Initialize Database

Run once to create tables:

```bash
python init_db.py
```

### 4. Start Server

```bash
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Authentication

#### POST `/auth/signup`
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "software_background": "Python, JavaScript, React",
  "hardware_background": "Arduino, Raspberry Pi"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "John Doe",
    "software_background": "Python, JavaScript, React",
    "hardware_background": "Arduino, Raspberry Pi",
    "email_verified": false,
    "created_at": "2024-01-01T00:00:00",
    "image": null,
    "role": "user"
  }
}
```

#### POST `/auth/login`
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** Same as signup.

#### GET `/auth/me`
Get current user profile (requires authentication).

**Headers:**
```
Authorization: Bearer <token>
```

#### PUT `/auth/me`
Update current user profile (requires authentication).

**Request:**
```json
{
  "name": "Updated Name",
  "software_background": "Updated background",
  "hardware_background": "Updated hardware"
}
```

#### POST `/auth/verify-token`
Verify if a token is valid.

**Headers:**
```
Authorization: Bearer <token>
```

## Usage Examples

### Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "name": "Test User",
    "password": "password123",
    "software_background": "Python developer",
    "hardware_background": "Robotics enthusiast"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get Profile (Authenticated)
```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-token>"
```

### Update Profile (Authenticated)
```bash
curl -X PUT http://localhost:8000/auth/me \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Name",
    "software_background": "Senior Python Developer"
  }'
```

## Protected Routes

The `/chat` endpoint now optionally accepts authentication. To make it required, change:

```python
current_user: Optional[User] = Depends(get_current_user)
```

to:

```python
current_user: User = Depends(get_current_user)
```

## Database Schema

### Users Table

```sql
CREATE TABLE users (
    id VARCHAR PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    name VARCHAR NOT NULL,
    password_hash VARCHAR NOT NULL,
    software_background TEXT,
    hardware_background TEXT,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    image VARCHAR,
    role VARCHAR DEFAULT 'user'
);
```

## Security Best Practices

1. **JWT Secret**: Use a strong, random secret key (min 32 characters)
2. **Password**: Minimum 8 characters enforced
3. **HTTPS**: Always use HTTPS in production
4. **Token Expiration**: Tokens expire after 7 days
5. **Password Hashing**: Uses bcrypt with automatic salt

## BetterAuth Compatibility

This implementation follows BetterAuth patterns:
- JWT token-based authentication
- User profile with custom fields
- RESTful API structure
- Standard HTTP status codes
- Bearer token authentication

Can be easily integrated with BetterAuth frontend if migrating to Next.js.


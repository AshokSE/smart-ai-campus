from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from .database import db
from .utils import hash_password, verify_password, create_jwt  # <-- using your utility functions

router = APIRouter()


# ------------------ MODELS ---------------------

class SignupModel(BaseModel):
    username: str
    email: str
    password: str


class LoginModel(BaseModel):
    email: str
    password: str


# ------------------ SIGNUP ROUTE ---------------------

@router.post("/signup")
async def signup(data: SignupModel):
    users = db.users

    # Check if email exists
    existing = await users.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pw = hash_password(data.password)

    # Insert user
    user_doc = {
        "username": data.username,
        "email": data.email,
        "password": hashed_pw,
    }

    result = await users.insert_one(user_doc)

    return {
        "status": "success",
        "message": "User registered successfully",
        "user_id": str(result.inserted_id)
    }


# ------------------ LOGIN ROUTE ---------------------

@router.post("/login")
async def login(data: LoginModel):
    users = db.users

    # Find user by email
    user = await users.find_one({"email": data.email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not verify_password(data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create JWT token
    token = create_jwt(str(user["_id"]))

    return {
        "status": "success",
        "message": "Login successful",
        "token": token,
        "user_id": str(user["_id"]),
        "username": user["username"]
    }

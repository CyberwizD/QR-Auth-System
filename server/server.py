from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import jwt
import bcrypt
import uuid
import qrcode
import io
import base64
from PIL import Image
import json
import asyncio

# Database Configuration
SQLALCHEMY_DATABASE_URL = "sqlite:///./qr_auth.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# JWT Configuration
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    devices = relationship("DeviceSession", back_populates="user")
    qr_sessions = relationship("QRSession", back_populates="user")

class DeviceSession(Base):
    __tablename__ = "device_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(String, unique=True, index=True)
    device_name = Column(String)
    session_token = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationship
    user = relationship("User", back_populates="devices")

class QRSession(Base):
    __tablename__ = "qr_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, unique=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_used = Column(Boolean, default=False)
    is_expired = Column(Boolean, default=False)
    device_info = Column(String, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="qr_sessions")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    is_active: bool

class DeviceSessionResponse(BaseModel):
    id: int
    device_id: str
    device_name: str
    created_at: datetime
    last_active: datetime
    is_active: bool

class QRSessionCreate(BaseModel):
    device_info: Optional[str] = None

class QRSessionResponse(BaseModel):
    session_id: str
    qr_code_data: str
    expires_at: datetime

class QRScanRequest(BaseModel):
    session_id: str

# FastAPI App
app = FastAPI(title="QR Authentication API", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
    
    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
    
    async def send_personal_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message)
            except:
                self.disconnect(session_id)

manager = ConnectionManager()

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return username
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def get_current_user(username: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def generate_qr_code(data: str) -> str:
    """Generate QR code and return as base64 string"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    return base64.b64encode(buffer.getvalue()).decode()

# API Endpoints

@app.post("/auth/register", response_model=UserResponse)
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/auth/login")
def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == user_data.username).first()
    
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User account is disabled")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )
    }

@app.get("/auth/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/qr/generate", response_model=QRSessionResponse)
def generate_qr_session(
    qr_data: QRSessionCreate,
    db: Session = Depends(get_db)
):
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Set expiration (5 minutes from now)
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Create QR session
    qr_session = QRSession(
        session_id=session_id,
        expires_at=expires_at,
        device_info=qr_data.device_info
    )
    
    db.add(qr_session)
    db.commit()
    
    # Generate QR code data (JSON string)
    qr_data_dict = {
        "session_id": session_id,
        "timestamp": datetime.utcnow().isoformat(),
        "expires_at": expires_at.isoformat()
    }
    qr_code_data = generate_qr_code(json.dumps(qr_data_dict))
    
    return QRSessionResponse(
        session_id=session_id,
        qr_code_data=qr_code_data,
        expires_at=expires_at
    )

@app.post("/qr/scan")
def scan_qr_code(
    scan_data: QRScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Find QR session
    qr_session = db.query(QRSession).filter(
        QRSession.session_id == scan_data.session_id
    ).first()
    
    if not qr_session:
        raise HTTPException(status_code=404, detail="QR session not found")
    
    # Check if session is expired
    if datetime.utcnow() > qr_session.expires_at:
        qr_session.is_expired = True
        db.commit()
        raise HTTPException(status_code=400, detail="QR code has expired")
    
    # Check if already used
    if qr_session.is_used:
        raise HTTPException(status_code=400, detail="QR code has already been used")
    
    # Mark session as used and associate with user
    qr_session.is_used = True
    qr_session.user_id = current_user.id
    db.commit()
    
    # Create device session
    device_id = str(uuid.uuid4())
    session_token = create_access_token(
        data={"sub": current_user.username, "device_id": device_id}
    )
    
    device_session = DeviceSession(
        user_id=current_user.id,
        device_id=device_id,
        device_name=qr_session.device_info or "Desktop Device",
        session_token=session_token
    )
    
    db.add(device_session)
    db.commit()
    
    # Send notification to desktop via WebSocket
    asyncio.create_task(manager.send_personal_message(
        json.dumps({
            "type": "login_success",
            "user": {
                "id": current_user.id,
                "username": current_user.username,
                "email": current_user.email
            },
            "session_token": session_token,
            "device_id": device_id
        }),
        scan_data.session_id
    ))
    
    return {
        "message": "Device linked successfully",
        "device_id": device_id,
        "session_token": session_token
    }

@app.get("/devices", response_model=List[DeviceSessionResponse])
def get_user_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    devices = db.query(DeviceSession).filter(
        DeviceSession.user_id == current_user.id,
        DeviceSession.is_active == True
    ).all()
    
    return devices

@app.delete("/devices/{device_id}")
def revoke_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    device = db.query(DeviceSession).filter(
        DeviceSession.device_id == device_id,
        DeviceSession.user_id == current_user.id
    ).first()
    
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    device.is_active = False
    db.commit()
    
    return {"message": "Device revoked successfully"}

# WebSocket Endpoint
@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    # Verify session exists
    qr_session = db.query(QRSession).filter(QRSession.session_id == session_id).first()
    if not qr_session:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back for keep-alive
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        manager.disconnect(session_id)

@app.get("/")
def root():
    return {
        "message": "QR Authentication API",
        "version": "1.0.0",
        "endpoints": {
            "register": "/auth/register",
            "login": "/auth/login",
            "me": "/auth/me",
            "generate_qr": "/qr/generate",
            "scan_qr": "/qr/scan",
            "devices": "/devices",
            "websocket": "/ws/{session_id}"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

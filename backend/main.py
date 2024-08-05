from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import bcrypt

# Конфигурация
SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# OAuth2 схема
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth")

# Фиктивная база данных пользователей
fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": bcrypt.hashpw("secret".encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        "disabled": False,
    }
}

# Фиктивная база данных для подтверждения кода регистрации и восстановления пароля
registration_codes_db = {}
password_reset_codes_db = {}
password_reset_tokens_db = {}

# Модель пользователя
class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

# Модель для токена
class Token(BaseModel):
    access_token: str
    token_type: str

# Модель для регистрации
class UserCreate(BaseModel):
    fstName: str
    scdName: str
    patronymic: Optional[str] = None
    birthdayDate: str
    tgNickname: str
    phone: Optional[str] = None
    email: str
    password: str

# Модель для второго шага регистрации
class RegistrationStep2(BaseModel):
    id: str
    code: str

# Модель для первого шага восстановления пароля
class PasswordResetStep1(BaseModel):
    email: str

# Модель для второго шага восстановления пароля
class PasswordResetStep2(BaseModel):
    email: str
    code: str

# Модель для третьего шага восстановления пароля
class PasswordResetStep3(BaseModel):
    password: str
    id: str

# Утилита для получения пользователя из базы данных
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

# Утилита для аутентификации пользователя
def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        return False
    return user

# Утилита для создания JWT токена
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Корневой эндпоинт
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application"}

# Эндпоинт для авторизации
@app.get("/api/v1/auth", response_model=Token)
def login_for_access_token(username: str = Query(...), password: str = Query(...)):
    user = authenticate_user(fake_users_db, username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Утилита для получения текущего пользователя
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = username
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data)
    if user is None:
        raise credentials_exception
    return user

# Эндпоинт для получения профиля
@app.get("/api/v1/profile", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

# Эндпоинт для регистрации
@app.post("/api/v1/reg1")
async def register_user(user: UserCreate):
    if user.email in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    registration_codes_db[user.email] = "123456"  # Фиктивный код, в реальной системе он должен быть сгенерирован и отправлен пользователю
    return {"status": "User created, please confirm your email", "id": user.email}

# Эндпоинт для второго шага регистрации
@app.post("/api/v1/reg2")
async def confirm_registration(step2: RegistrationStep2):
    if step2.id not in registration_codes_db or registration_codes_db[step2.id] != step2.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid confirmation code",
        )
    del registration_codes_db[step2.id]
    return {"status": "User confirmed"}

# Эндпоинт для первого шага восстановления пароля
@app.post("/api/v1/forgot-password1")
async def forgot_password_step1(request: PasswordResetStep1):
    if request.email not in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found",
        )
    password_reset_codes_db[request.email] = "654321"  # Фиктивный код, в реальной системе он должен быть сгенерирован и отправлен пользователю
    return {"status": "Password reset code sent"}

# Эндпоинт для второго шага восстановления пароля
@app.post("/api/v1/forgot-password2")
async def forgot_password_step2(request: PasswordResetStep2):
    if request.email not in password_reset_codes_db or password_reset_codes_db[request.email] != request.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset code",
        )
    reset_id = f"reset-{request.email}"  # Фиктивный ID восстановления пароля
    password_reset_tokens_db[reset_id] = request.email
    del password_reset_codes_db[request.email]
    return {"status": "Password reset code confirmed", "id": reset_id}

# Эндпоинт для третьего шага восстановления пароля
@app.post("/api/v1/forgot-password3")
async def forgot_password_step3(request: PasswordResetStep3):
    email = password_reset_tokens_db.get(request.id)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset ID",
        )
    user = fake_users_db.get(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not found",
        )
    user['hashed_password'] = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    del password_reset_tokens_db[request.id]
    return {"status": "Password reset successfully"}

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

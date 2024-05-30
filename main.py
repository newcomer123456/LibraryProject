import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Form, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette.templating import Jinja2Templates
from starlette.responses import RedirectResponse
from database.ORM import ORM
from database.models import Book, User
from typing import Annotated
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import logging
import traceback

app = FastAPI(title="MenegerLibrary")
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "19109197bd5e7c289b92b2b355083ea26c71dee2085ceccc19308a7291b2ea06"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Визначення авторизації через OAuth2BearerToken
security = OAuth2PasswordBearer(tokenUrl="/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("uvicorn.error")

def token_create(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    encoded_jwt = None
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=404, detail="User not found")
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@app.post("/token")
async def token_get(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data = ORM.get_user_by_username(form_data.username)
    if not user_data:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    else:
        global user
        user = user_data
        # Перевірка хешів паролів на ідентичність
        if not pwd_context.verify(form_data.password, user.password):
            raise HTTPException(status_code=400, detail="Incorrect username or password")
        # Аутентифікація пройдена - створюємо токен
        token = token_create(data={"sub": user.username})

    return {"access_token": token, "token_type": "bearer"}


@app.post("/add_user")
def add_user(username: str, password: str):
    user = User(username=username, password=pwd_context.hash(password))
    ORM.add_record(user)
    return {"message": "User has been added successfully"}

@app.get("/add_user")
def add_user(request: Request):
    return templates.TemplateResponse("add_user.html", {"request": request})
    


@app.get("/secure-endpoint/")
def secure_endpoint(username: str = Depends(get_current_user)):
    return {"message": f"Hello, {username}! You are authorized."}


@app.post("/add_book")
def add_book(
    request: Request,
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    description: Annotated[str, Form()],
    num_pages: Annotated[int, Form()],
    username: str = Depends(get_current_user)
):
    book = Book(title=title, author=author, description=description, num_pages=num_pages)
    ORM.add_record(book)
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/add_book")
def add_book_form(request: Request, username: str = Depends(get_current_user)):
    return templates.TemplateResponse("add_book.html", {"request": request})

@app.get("/index")
def index(request: Request, username: str = Depends(get_current_user)):
    books = ORM.get_all_books()
    return templates.TemplateResponse("index.html", {"request": request, "books": books})

@app.get("/books/{book_id}")
def read_book(book_id: int, request: Request, username: str = Depends(get_current_user)):
    try:
        book = ORM.get_book_by_id(book_id)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        return templates.TemplateResponse("book_detail.html", {"request": request, "book": book})
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/delete_book")
def delete_book(request: Request, title: Annotated[str, Form()], method: Annotated[str, Form()] = "delete", username: str = Depends(get_current_user)):
    if method.lower() == "delete":
        book = ORM.get_book_by_title(title)
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        ORM.remove_book_by_id(book.id)
    return RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete_book")
def delete_book(request: Request):
    return templates.TemplateResponse("delete_book.html", {"request": request})

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_data = ORM.get_user_by_username(form_data.username)
    if not user_data or not pwd_context.verify(form_data.password, user_data.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Incorrect username or password"})
    
    token = token_create(data={"sub": user_data.username})
    response = RedirectResponse(url="/index", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(key="access_token", value=token, httponly=True)
    return response

@app.get("/")
def root():
    return RedirectResponse(url="/login")

uvicorn.run(app, port=8005)
from os import access
from fastapi import APIRouter,status
from fastapi.exceptions import HTTPException
from database import SessionLocal, engine
from schemas import SignUpModel, LoginModel
from models import User
from sqlalchemy.orm import Session
from fastapi import Depends
from werkzeug.security import generate_password_hash, check_password_hash
from fastapi_jwt_auth import AuthJWT
from fastapi.encoders import jsonable_encoder

auth_router=APIRouter(
    prefix='/auth',
    tags=['auth']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



session=SessionLocal(bind=engine)
@auth_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## Sample hello world route
    
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )

    return {"message" : "Hello World"}



# Example usage in the route
@auth_router.post('/signup', response_model=SignUpModel, status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel, db: Session = Depends(get_db)):
    """
        ## Create a user
        This requires the following
        ```
                username:int
                email:str
                password:str
                is_staff:bool
                is_active:bool

        ```
    
    """
    db_email = db.query(User).filter(User.email == user.email).first()

    if db_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the email already exists")

    db_username = db.query(User).filter(User.username == user.username).first()

    if db_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="User with the username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_staff=user.is_staff,
        is_active=user.is_active
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # Refresh to get the new user's ID if needed

    return jsonable_encoder(new_user)

#login route

@auth_router.post('/login', status_code=200)
async def login(user: LoginModel, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    """     
        ## Login a user
        This requires
            ```
                username:str
                password:str
            ```
        and returns a token pair `access` and `refresh`
    """
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user and check_password_hash(db_user.password, user.password): # type: ignore
        access_token = Authorize.create_access_token(subject=db_user.username) # type: ignore
        refresh_token = Authorize.create_refresh_token(subject=db_user.username) # type: ignore

        response = {
            "access": access_token,
            "refresh": refresh_token
        }
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Username or Password"
    )

#refreshing tokens

@auth_router.get('/refresh')
async def refresh_token(Authorize:AuthJWT=Depends()):
    """
    ## Create a fresh token
    This creates a fresh token. It requires an refresh token.
    """
    try:
        Authorize.jwt_refresh_token_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please provide a valid refresh token"
        )
    
    current_user=Authorize.get_jwt_subject()

    access_token=Authorize.create_access_token(subject=current_user) # type: ignore

    return jsonable_encoder({"access":access_token})




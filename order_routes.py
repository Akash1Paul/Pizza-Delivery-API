from fastapi import APIRouter, Depends,status
from fastapi_jwt_auth import AuthJWT
from models import User, Order
from schemas import OrderModel, OrderStatusModel
from fastapi.exceptions import HTTPException
from database import SessionLocal
from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

order_router=APIRouter(
     prefix='/order',
    tags=['order']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@order_router.get('/')
async def hello(Authorize:AuthJWT=Depends()):
    """
        ## A sample hello world route
        This returns Hello world
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )

    return {"message" : "Hello World"}

@order_router.post('/order',status_code=status.HTTP_201_CREATED)
async def place_an_order(order:OrderModel, Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Placing an Order
        This requires the following
        - quantity : integer
        - pizza_size: str
    
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )
    current_user=Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username==current_user).first()

    new_order=Order(
        pizza_size=order.pizza_size,
        quantity=order.quantity
    )

    new_order.user=user
    db.add(new_order)
    db.commit()

    response={
        "id":new_order.id,
        "pizza_size":new_order.pizza_size,
        "quantity":new_order.quantity,
        "order_status":new_order.order_status
    }
    
    return jsonable_encoder(response)

@order_router.get('/order')
async def list_all_orders(Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## List all orders
        This lists all  orders made. It can be accessed by superusers
        
    
    """
    try:
        Authorize.jwt_required()

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )
    current_user=Authorize.get_jwt_subject()
    user = db.query(User).filter(User.username==current_user).first()

    if user.is_staff: # type: ignore
        orders=db.query(Order).all()
        return jsonable_encoder(orders)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not a superuser"
        )

@order_router.get('/orders/{id}')
async def get_order_by_id(id:int, Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Get an order by its ID
        This gets an order by its ID and is only accessed by a superuser
        

    """
    try:
        Authorize.jwt_required()
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )
    user=Authorize.get_jwt_subject()

    current_user=db.query(User).filter(User.username==user).first()

    if current_user.is_staff: # type: ignore
        order=db.query(Order).filter(Order.id==id).first()

        return jsonable_encoder(order)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="User not alowed to carry out request"
        )

#get current user order
@order_router.get('/user/orders')
async def get_user_order(Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Get a current user's orders
        This lists the orders made by the currently logged in users
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Invalid Token"
        )
    user=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==user).first()

    return jsonable_encoder(current_user.orders) # type: ignore

#get specific order
@order_router.get('/user/order/{id}/')
async def get_specific_order(id:int,Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Get a specific order by the currently logged in user
        This returns an order by ID for the currently logged in user
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )

    subject=Authorize.get_jwt_subject()

    current_user=db.query(User).filter(User.username==subject).first()

    orders=current_user.orders # type: ignore

    for o in orders:
        if o.id == id:
            return jsonable_encoder(o)
    
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
        detail="No order with such id"
    )

@order_router.put('/order/update/{id}/')
async def update_order(id:int,order:OrderModel,Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Updating an order
        This udates an order and requires the following fields
        - quantity : integer
        - pizza_size: str
    
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    order_to_update=db.query(Order).filter(Order.id==id).first()

    order_to_update.quantity=order.quantity # type: ignore
    order_to_update.pizza_size=order.pizza_size # type: ignore

    db.commit()
    
    response={
                "id":order_to_update.id, # type: ignore
                "quantity":order_to_update.quantity, # type: ignore
                "pizza_size":order_to_update.pizza_size, # type: ignore
                "order_status":order_to_update.order_status, # type: ignore
            }
    return jsonable_encoder(order_to_update)
    

@order_router.patch('/order/update/{id}')
async def update_order_status(id:int,order:OrderStatusModel,Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Update an order's status
        This is for updating an order's status and requires ` order_status ` in str format
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    username=Authorize.get_jwt_subject()
    current_user=db.query(User).filter(User.username==username).first()

    if current_user.is_staff: # type: ignore
        order_to_update=db.query(Order).filter(Order.id==id).first()
        order_to_update.order_status = order.order_status # type: ignore

        db.commit()
        response={
                "id":order_to_update.id, # type: ignore
                "quantity":order_to_update.quantity, # type: ignore
                "pizza_size":order_to_update.pizza_size, # type: ignore
                "order_status":order_to_update.order_status, # type: ignore
            }
        return jsonable_encoder(response)
    
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not a superuser"
        )

@order_router.delete('/order/delete/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_an_order(id:int,Authorize:AuthJWT=Depends(), db: Session = Depends(get_db)):
    """
        ## Delete an Order
        This deletes an order by its ID
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    
    order_to_delete=db.query(Order).filter(Order.id==id).first()

    db.delete(order_to_delete)

    db.commit()

    return order_to_delete
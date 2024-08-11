from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import List, Generator, AsyncGenerator
from contextlib import asynccontextmanager
from product_service.models import Product, Product_Create, Product_Update
from typing import Annotated , Dict , Any
from product_service.db import create_tables, get_session
from product_service.setting import BOOTSTRAP_SERVER, KAFKA_PRODUCT_CREATE_TOPIC


async def create_topic():
    admin_client = AIOKafkaAdminClient(
        bootstrap_servers=BOOTSTRAP_SERVER)
    await admin_client.start()
    topic_list = [NewTopic(name=KAFKA_PRODUCT_CREATE_TOPIC,
                           num_partitions=2, replication_factor=1)]
    try:
        await admin_client.create_topics(new_topics=topic_list, validate_only=False)
        print(f"Topic '{KAFKA_PRODUCT_CREATE_TOPIC}' created successfully")
    except Exception as e:
        print(f"Failed to create topic '{KAFKA_PRODUCT_CREATE_TOPIC}': {e}")
    finally:
        await admin_client.close()


async def get_kafka_producer():
    producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVER)
    await producer.start()
    try:
        yield producer
    finally:
        await producer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print('Creating Tables')
    create_tables()
    print("Tables Created")
    yield

app = FastAPI(lifespan=lifespan, title="Product App", version='1.0.0')


@app.get('/')
async def root() -> Any:
    return {"message": "Welcome to the Product app"}


@app.post('/create_products/', response_model=Product)
async def create_product(producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)], 
                         product: Product_Create, 
                         session: Annotated[Session, Depends(get_session)]) -> Product:

    new_product = Product(name=product.name, price=product.price, quantity=product.quantity)

    order_created_message = Product_Create(
            name=product.name, price=product.price, quantity=product.quantity
    )

    message_bytes = order_created_message.SerializeToString()

    await producer.send_and_wait(KAFKA_PRODUCT_CREATE_TOPIC, message_bytes)
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product




# @app.get('/products/', response_model=List[Product])
# async def get_all_products(session: Session = Depends(get_session)) -> List[Product]:
#     products = list(session.exec(select(Product)).all())
#     if products:
#         return products
#     else:
#         raise HTTPException(status_code=404, detail="No products found")


# @app.get('/products/{id}', response_model=Product)
# async def get_single_product(id: int, session: Session = Depends(get_session)) -> Product:
#     product = session.get(Product, id)
#     if product:
#         return product
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")

# @app.put('/products/{id}', response_model=Product)
# async def edit_product(id: int, product: Product_Update, session: Session = Depends(get_session)) -> Product:
#     existing_product = session.get(Product, id)
#     if existing_product:
#         existing_product.name = product.name
#         existing_product.price = product.price
#         existing_product.quantity = product.quantity
#         session.add(existing_product)
#         session.commit()
#         session.refresh(existing_product)
#         return existing_product
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")

# @app.delete('/products/{id}')
# async def delete_product(id: int, session: Session = Depends(get_session)) -> Any:
#     product = session.get(Product, id)
#     if product:
#         session.delete(product)
#         session.commit()
#         return {"message": "Product successfully deleted"}
#     else:
#         raise HTTPException(status_code=404, detail="Product not found")
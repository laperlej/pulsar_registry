from http import HTTPStatus
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from models.model import Pulsar, User, Outbox, Message
from pydantic import BaseModel, EmailStr

router = APIRouter()

class GetPulsarResponse(BaseModel):
    id: int
    url: str
    api_key: str
    users: list[str]

@router.get("/api/pulsar/{id}", status_code=HTTPStatus.OK)
async def get_pulsar(request: Request, id: int) -> GetPulsarResponse:
    with request.app.state.db.get_session() as session:
        result = session.execute(select(Pulsar).where(Pulsar.id == id))
        pulsar = result.scalar_one_or_none()
        if pulsar is None:
            raise HTTPException(status_code=404, detail="Pulsar not found")
        response = GetPulsarResponse(
            id=pulsar.id,
            url=pulsar.url,
            api_key=pulsar.api_key,
            users=[user.email for user in pulsar.users],
        )
        return response

@router.get("/api/pulsar", status_code=HTTPStatus.OK)
async def search_pulsar(request: Request, user = None):
    if user is None:
        raise HTTPException(status_code=400, detail="User not provided")
    with request.app.state.db.get_session() as session:
        result = session.execute(select(Pulsar).where(Pulsar.users.any(User.email == user)))
        pulsars = result.scalars().all()
        return [GetPulsarResponse(
            id=pulsar.id,
            url=pulsar.url,
            api_key=pulsar.api_key,
            users=[user.email for user in pulsar.users],
        ) for pulsar in pulsars]

class CreatePulsarBody(BaseModel):
    url: str
    api_key: str
    users: list[str]

    model_config = {"from_attributes": True}

class CreatePulsarResponse(BaseModel):
    id: int

@router.post("/api/pulsar", status_code=HTTPStatus.CREATED)
async def create_pulsar(request: Request, pulsar: CreatePulsarBody) -> CreatePulsarResponse:
    with request.app.state.db.get_session() as session:
        print(f"Creating pulsar: {pulsar}")
        users = session.query(User).filter(User.email.in_(pulsar.users)).all()
        users = []
        for email in pulsar.users:
            result = session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                print(f"Creating user: {email}")
                user = User(email=email)
                session.add(user)
            users.append(user)
        session.flush()
        
        # Create new pulsar
        new_pulsar = Pulsar(url=pulsar.url, api_key=pulsar.api_key, users=users)
        session.add(new_pulsar)
        session.flush()

        # Create new outbox
        for user in new_pulsar.users:
            new_outbox = Outbox(message=Message.CREATED, user_id=user.id, pulsar_id=new_pulsar.id)
            session.add(new_outbox)

        session.commit()
        return CreatePulsarResponse(id=new_pulsar.id)

@router.put("/api/pulsar/{pulsar_id}", status_code=HTTPStatus.OK)
async def update_pulsar(request: Request, pulsar_id: int, pulsar: CreatePulsarBody) -> CreatePulsarResponse:
    with request.app.state.db.get_session() as session:
        # First, check if pulsar exists
        result = session.execute(select(Pulsar).where(Pulsar.id == pulsar_id))
        existing_pulsar = result.scalar_one_or_none()
        if existing_pulsar is None:
            raise HTTPException(status_code=404, detail="Pulsar not found")

        # Process users
        users = []
        for email in pulsar.users:
            result = session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(email=email)
                session.add(user)
            users.append(user)
        
        # Update existing pulsar
        existing_pulsar.url = pulsar.url
        existing_pulsar.api_key = pulsar.api_key
        existing_pulsar.users = users
        
        # Create new outbox
        for user in existing_pulsar.users:
            new_outbox = Outbox(message=Message.CREATED, user_id=user.id, pulsar_id=existing_pulsar.id)
            session.add(new_outbox)

        session.commit()
        session.refresh(existing_pulsar)
        return CreatePulsarResponse(id=existing_pulsar.id)

class DeleteResponse(BaseModel):
    pulsar_id: int

@router.delete("/api/pulsar/{pulsar_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_pulsar(request: Request, pulsar_id: int):
    with request.app.state.db.get_session() as session:
        result = session.execute(select(Pulsar).where(Pulsar.id == pulsar_id))
        pulsar = result.scalar_one_or_none()
        if pulsar is None:
            raise HTTPException(status_code=404, detail="Pulsar not found")

        # create new outbox
        for user in pulsar.users:
            new_outbox = Outbox(message=Message.DELETED, user_id=user.id, pulsar_id=pulsar.id)
            session.add(new_outbox)

        # Delete pulsar
        session.delete(pulsar)

        session.commit()
        return None 


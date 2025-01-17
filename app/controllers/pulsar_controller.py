from http import HTTPStatus
from fastapi import APIRouter, Request, HTTPException
from sqlalchemy import select
from app.models.model import Pulsar, User
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
    users: list[EmailStr]

    model_config = {"from_attributes": True}

class CreatePulsarResponse(BaseModel):
    id: int

@router.post("/api/pulsar", status_code=HTTPStatus.CREATED)
async def create_pulsar(request: Request, pulsar: CreatePulsarBody) -> CreatePulsarResponse:
    with request.app.state.db.get_session() as session:
        users = session.query(User).filter(User.email.in_(pulsar.users)).all()
        users = []
        for email in pulsar.users:
            result = session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            if user is None:
                user = User(email=email)
                session.add(user)
            users.append(user)
        
        new_pulsar = Pulsar(url=pulsar.url, api_key=pulsar.api_key, users=users)
        session.add(new_pulsar)
        session.commit()
        session.refresh(new_pulsar)
        return CreatePulsarResponse(id=new_pulsar.id)

class DeleteResponse(BaseModel):
    pulsar_id: int

@router.delete("/api/pulsar/{pulsar_id}", status_code=HTTPStatus.NO_CONTENT)
async def delete_pulsar(request: Request, pulsar_id: int):
    with request.app.state.db.get_session() as session:
        result = session.execute(select(Pulsar).where(Pulsar.id == pulsar_id))
        pulsar = result.scalar_one_or_none()
        if pulsar is None:
            raise HTTPException(status_code=404, detail="Pulsar not found")
        session.delete(pulsar)
        session.commit()
        return None 


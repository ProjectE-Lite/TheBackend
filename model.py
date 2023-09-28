from pydantic import BaseModel
from typing import Optional


class Recruiters(BaseModel):
    username: str
    password: str
    name: str
    address: str
    credit: int
    email: str
    list_of_work: list
    have_worked_with: dict
    notification: list
    list_of_money_exchange: list

class Users(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    nick_name: str
    gender: str
    age: int
    birth_date: str
    tel: str
    email: str
    line_id: str
    point: float
    address: str
    credit: int
    resume: str
    list_of_money_exchange: list
    list_of_work: list
    field_of_interested: dict
    notification: list
    feedback: dict

class Works(BaseModel):
    recruiter_id: int
    name: str
    type_of_work: str
    number_requirement: int
    work_description: dict
    hourly_income: int
    pot: int
    list_of_candidate: list
    list_of_worker: list
    end_registeration: str
    work_date: str
    start_time: str
    end_time: str
    user_status: dict

class Reviews(BaseModel):
    recruiter_id: int
    score: int
    text: str



class RecruitersRequest(BaseModel):
    username: str
    password: str
    name: str
    address: str
    credit: int
    email: str
    list_of_work: list
    have_worked_with: dict
    notification: list
    list_of_money_exchange: list

class UsersRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    nick_name: str
    gender: str
    age: int
    birth_date: str
    tel: str
    email: str
    line_id: str
    point: float
    address: str
    credit: int
    resume: str
    list_of_money_exchange: list
    list_of_work: list
    field_of_interested: dict
    notification: list
    feedback: dict

class WorksRequest(BaseModel):
    name: str
    type_of_work: str
    number_requirement: int
    work_description: dict
    hourly_income: int
    list_of_candidate: list
    list_of_worker: list
    end_registeration: str
    work_date: str
    start_time: str
    end_time: str
    user_status: dict

class ReviewsRequest(BaseModel):
    score: int
    text: str

class Login(BaseModel):
    username: str
    password: str



class UpdateUsers(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    nick_name: Optional[str]
    gender: Optional[str]
    age: Optional[int]
    birth_date: Optional[str]
    tel: Optional[str]
    email: Optional[str]
    line_id: Optional[str]
    address: Optional[str]

class UpdateWorks(BaseModel):
    name: Optional[str] 
    type_of_work: Optional[str]
    number_requirement: Optional[int]
    work_description: Optional[dict]
    hourly_income: Optional[int]
    end_registeration: Optional[str]
    work_date: Optional[str]
    start_time: Optional[str]
    end_time: Optional[str]
    user_status: Optional[dict]
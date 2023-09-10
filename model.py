from pydantic import BaseModel


class Recruiters(BaseModel):
    recruiter_id: int
    name: str
    address: str
    credit: int
    email: str
    list_of_work: list
    have_worked_with: dict
    notification: list
    list_of_money_exchange: list

class Users(BaseModel):
    user_id: int
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
    work_id: int
    recruiter_id: int
    name: str
    type_of_work: str
    number_requirement: int
    work_description: str
    hourly_income: int
    pot: int
    list_of_candidiate: list
    list_of_worker: list
    end_registeration: str
    work_date: str
    work_day: str
    start_time: str
    end_time: str
    user_status: dict
    

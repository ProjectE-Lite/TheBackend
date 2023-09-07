from fastapi import FastAPI
from pydantic import BaseModel
from model import *
from recruiterManagement import *
from userManagement import *
from workManagement import *

app = FastAPI()



@app.get("/test/{test_id}/collections/{kuy_id}")
async def testo(test_id: str, kuy_id: str):
    return {"kuy" : test_id,
            "mha" : kuy_id
            }


@app.post("/recruiters/insert_recruiter")
async def insert_pseudo_recruiter(recruiter: Recruiters):
    insertPseudoRecruiter(vars(recruiter))
    return "success you have inserted recruiter"


@app.post("/users/insert_users")
async def insert_pseudo_user(user: Users):
    insertPseudoUser(vars(user))
    return "success you have inserted user"


@app.post("/works/create_work/{recruiter_id}")
async def insert_pseudo_work(work: Works, recruiter_id: int):
    return insertPseudoWork(vars(work), recruiter_id)
    


@app.get("/works/{work_date}")
async def get_work_by_work_date(work_date: str):
    return getWorkByWorkDate(work_date)
   

@app.get("/users/get_work_details/{work_id}")
async def get_work_details_by_work_id(work_id: int):
    return getWorkByWorkID(work_id)



@app.post("/users/applyButt/{user_id}/{work_id}")
async def apply_button(user_id: int, work_id: int):
    # addUserToListOfCandidate()
    # addWorkToListOfWork()
    # notiUserAppToRecruiter()
    # updateUserStatusInWork()
    pass
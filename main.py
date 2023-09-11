from fastapi import FastAPI
from pydantic import BaseModel
from database import *
from model import *
from recruiterManagement import *
from userManagement import *
from workManagement import *
from helpingFunction import *

app = FastAPI()


@app.get("/gen12datenext")
async def gen12datenext():
    return genNext12Days()


@app.post("/recruiters")
async def insert_pseudo_recruiter(recruiter: Recruiters):
    insertPseudoRecruiter(vars(recruiter))
    return "success you have inserted recruiter"


@app.post("/users")
async def insert_pseudo_user(user: Users):
    insertPseudoUser(vars(user))
    return "success you have inserted user"


@app.post("/works/{recruiter_id}")
async def insert_pseudo_work(work: Works, recruiter_id: int):
    # notiFieldOfInteresterd()
    return insertPseudoWork(vars(work), recruiter_id)


@app.get("/works/{work_id}")
async def get_work_by_work_id(work_id: int):
    return getWorkByWorkID(work_id)


@app.get("/work_date/{work_date}")
async def get_work_by_work_date(work_date: str):
    return getWorkByWorkDate(work_date)


@app.get("/works/{work_id}/manageWorker")
async def manage_user_in_work(work_id: int):
    return manageUserInWork(work_id)


@app.get("/users/{user_id}/allwork")
async def get_all_work_in_user(user_id: int):
    return getAllWorkInUser(user_id)


@app.get("/users/{user_id}/workinfo/{work_id}")
async def get_work_details_by_work_id(work_id: int, user_id: int):
    return getWorkDetailsByWorkId(work_id, user_id)


@app.get("/users/{user_id}/noti")
async def get_user_notification(user_id: int):
    return getUserNotification(user_id)


@app.get("/users/{user_id}")
async def get_user_detail(user_id: int):
    return getUserDetail(user_id)


@app.get("/users/{user_id}/stars/{point}")
async def get_review_by_stars(user_id: int, point: int):
    return getReviewByStars(user_id, point)


@app.get("/works/{work_id}/worker")
async def get_list_of_worker(work_id: int):
    return getListOfWorker(work_id)


@app.patch("/works/{work_id}")
async def update_work(work_id: int , work: UpdateWorks):
    updateDetailWork(work_id,work.dict(exclude_unset = True))
    return "success, you have updated work"


@app.patch("/users/{user_id}/apply/{work_id}")
async def apply_button(user_id: int, work_id: int):
    addUserToListOfCandidate(work_id, user_id)
    addWorkToListOfWork(work_id, user_id)
    initUserStatus(work_id, user_id)
    # notiUserAppToRecruiter()
    
    pass


@app.patch("/users/{user_id}/accept/{work_id}")
async def accept_button(user_id: int, work_id: int):
    AcceptButton(user_id, work_id)


@app.patch("/users/{user_id}/appoint/{work_id}/{date}/{time}")
async def appointment_button(user_id: int, work_id: int, date: str, time: str):
    AppointmentButton(user_id, work_id, date, time)


@app.patch("/users/{user_id}/payment/{work_id}")
async def payment_method(work_id: int, user_id: int, review_body: Reviews):
    addHaveWorkedWith(work_id, user_id)
    manageReview(user_id, work_id, vars(review_body))
    manageMoneyExchange(work_id, user_id)


@app.patch("/users/{user_id}/absent")
async def byebye_user_credit(user_id: int):
    return byebyeUserCredit(user_id)
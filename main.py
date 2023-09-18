from fastapi import FastAPI, Depends
from pydantic import BaseModel
from database import *
from model import *
from recruiterManagement import *
from userManagement import *
from workManagement import *
from helpingFunction import *
from auth.jwt_handler import *
from auth.jwt_bearer import *

app = FastAPI()

# if any function need authentication, simply add "dependencies=[Depends(jwtBearer())]" in endpoint
# Example: @app.get("/works/{work_id}") --> @app.get("/works/{work_id}", dependencies=[Depends(jwtBearer())])

@app.get("/12datenext")
async def gen12datenext():
    return genNext12Days()


@app.post("/recruiters", tags=["Recruiters"])
async def insert_pseudo_recruiter(recruiter: RecruitersRequest):
    insertPseudoRecruiter(vars(recruiter))
    return signJWT(recruiter.username)


@app.post("/users", tags=["Users"])
async def insert_pseudo_user(user: UsersRequest):
    insertPseudoUser(vars(user))
    return signJWT(user.username)


@app.post("/recruiters/{recruiter_id}/works", tags=["Recruiters"])
async def insert_pseudo_work(work: WorksRequest, recruiter_id: int):
    # notiFieldOfInteresterd()
    return insertPseudoWork(vars(work), recruiter_id)


@app.post("/recruiters/login", tags=["Recruiters"])
async def recruiter_login(recruiter: Login):
    if check_recruiter(recruiter.username, recruiter.password):
        return signJWT(recruiter.username)
    else:
        raise HTTPException(status_code=400, detail="Invalid login details")


@app.post("/users/login", tags=["Users"])
async def user_login(user: Login):
    if check_user(user.username, user.password):
        return signJWT(user.username)
    else:
        raise HTTPException(status_code=400, detail="Invalid login details")


@app.get("/works/{work_id}")
async def get_work_by_work_id(work_id: int):
    return getWorkByWorkID(work_id)


@app.get("/work_date/{work_date}")
async def get_work_by_work_date(work_date: str):
    return getWorkByWorkDate(work_date)


@app.get("/works/{work_id}/manageWorker")
async def manage_user_in_work(work_id: int):
    return manageUserInWork(work_id)


@app.get("/users/{user_id}/works")
async def get_all_work_in_user(user_id: int):
    return getAllWorkInUser(user_id)


@app.get("/users/{user_id}/works/{work_id}")
async def get_work_details_by_work_id(work_id: int, user_id: int):
    return getWorkDetailsByWorkId(work_id, user_id)


@app.get("/users/{user_id}/noti")
async def get_user_notification(user_id: int):
    return getUserNotification(user_id)


@app.get("/users/{user_id}")
async def get_user_detail(user_id: int):
    return getUserDetail(user_id)


@app.get("/users/{user_id}/review_points/{point}")
async def get_review_by_points(user_id: int, point: int):
    return getReviewByPoints(user_id, point)


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
async def payment_method(work_id: int, user_id: int, review_body: ReviewsRequest):
    addHaveWorkedWith(work_id, user_id)
    manageReview(user_id, work_id, vars(review_body))
    manageMoneyExchange(work_id, user_id)


@app.patch("/users/{user_id}/absent")
async def penalized_user_credit(user_id: int):
    return penalizedUserCredit(user_id)
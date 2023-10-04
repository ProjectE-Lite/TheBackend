from fastapi import FastAPI, Depends, File, UploadFile
from pydantic import BaseModel
from database import *
from model import *
from recruiterManagement import *
from userManagement import *
from workManagement import *
from helpingFunction import *
from auth.jwt_handler import *
from auth.jwt_bearer import *
import cloudinary.uploader

app = FastAPI()

RecruitersReq_checker = DataChecker("recruitersReq")
UsersUp_checker = DataChecker("usersUp")

# if any function need authentication, simply add "dependencies=[Depends(jwtBearer())]" in endpoint
# Example: @app.get("/works/{work_id}") --> @app.get("/works/{work_id}", dependencies=[Depends(jwtBearer())])

@app.get("/12datenext")
async def gen12datenext():
    return genNext12Days()


@app.post("/recruiters", tags=["Recruiters"])
async def insert_pseudo_recruiter(recruiter: RecruitersRequest = Depends(RecruitersReq_checker), file: UploadFile = File(...)):
    rid = insertPseudoRecruiter(vars(recruiter))
    result = cloudinary.uploader.upload(file.file, public_id = str(rid))
    url = result.get("url")
    https_url = url[:4] + 's' + url[4:]
    RecruitersCollection.update_one({"_id": rid}, {"$set": {"image": https_url}})
    return {"access token": signJWT(recruiter.username), "data": {"recruiter_id": str(rid)}}


@app.post("/users", tags=["Users"])
async def insert_pseudo_user(user: UsersRequest):
    insertPseudoUser(vars(user))
    uinfo = check_user(user.username, user.password)
    return {"access token": signJWT(user.username), "data": {"user_id": str(uinfo["_id"])}}


@app.post("/recruiters/{recruiter_id}/works", tags=["Recruiters"])
async def insert_pseudo_work(work: WorksRequest, recruiter_id: str):
    # notiFieldOfInteresterd()
    return insertPseudoWork(vars(work), recruiter_id)


@app.post("/recruiters/login", tags=["Recruiters"])
async def recruiter_login(recruiter: Login):
    if check_recruiter(recruiter.username, recruiter.password):
        rinfo = check_recruiter(recruiter.username, recruiter.password)
        return {"access token": signJWT(recruiter.username), "data": {"recruiter_id": str(rinfo["_id"])}}
    else:
        raise HTTPException(status_code=400, detail="Invalid login details")


@app.post("/users/login", tags=["Users"])
async def user_login(user: Login):
    if check_user(user.username, user.password):
        uinfo = check_user(user.username, user.password)
        return {"access token": signJWT(user.username), "data": {"user_id": str(uinfo["_id"])}}
    else:
        raise HTTPException(status_code=400, detail="Invalid login details")


@app.get("/works/{work_id}")
async def get_work_by_work_id(work_id: str):
    return getWorkByWorkID(work_id)


@app.get("/work_date/{work_date}")
async def get_work_by_work_date(work_date: str):
    return getWorkByWorkDate(work_date)


@app.get("/works/{work_id}/status")
async def get_work_status_and_list_of_user(work_id: str):
    return getWorkStatusAndListOfUser(work_id)


@app.get("/works/{work_id}/candidate")
async def get_candidate_of_work(work_id: str):
    return getCandidateOfWork(work_id)


@app.get("/works/{work_id}/worker")
async def get_list_of_worker(work_id: str):
    return getListOfWorker(work_id)


@app.get("/users/{user_id}")
async def get_user_detail(user_id: str):
    return getUserDetail(user_id)

@app.get("/recruiters/{recruiter_id}")
async def get_recruiter_detail(recruiter_id: str):
    return getRecruiterDetail(recruiter_id)


@app.get("/users/{user_id}/works")
async def get_all_work_in_user(user_id: str):
    return getAllWorkInUser(user_id)


@app.get("/users/{user_id}/works/{work_id}")
async def get_work_details_by_work_and_user_id(work_id: str, user_id: str):
    return getWorkDetailsByWorkAndUserId(work_id, user_id)


@app.get("/recruiters/{recruiter_id}/works")
async def get_all_work_in_recruiter(recruiter_id: str):
    return getAllWorkInRecruiter(recruiter_id)


@app.get("/recruiters/{recruiter_id}/work_date/{work_date}")
async def get_rec_work_by_date(recruiter_id: str,work_date: str):
   return getRecWorkFromListByDate(recruiter_id,work_date)


@app.get("/users/{user_id}/noti")
async def get_user_notification(user_id: str):
    return getUserNotification(user_id)


@app.get("/recruiters/{recruiter_id}/noti")
async def get_recruiter_notification(recruiter_id: str):
    return getRecruiterNotification(recruiter_id)


@app.get("/users/{user_id}/review_points/{point}")
async def get_review_by_points(user_id: str, point: int):
    return getReviewByPoints(user_id, point)


@app.get("/users/{user_id}/money_exchange")
async def get_user_list_of_money_exchange(user_id: str):
    return getUserListOfMoneyExchange(user_id)


@app.get("/users/noti/{noti_id}")
async def get_user_noti_detail(noti_id: str):
    return getUserNotiDetail(noti_id)


@app.get("/recruiters/noti/{noti_id}")
async def get_recruiter_noti_detail(noti_id: str):
    return getRecNotiDetail(noti_id)


@app.get("/users/status/{status_id}")
async def get_user_status(status_id: str):
    return getUserStatus(status_id)


@app.get("/money_exchange/{exchange_id}")
async def get_money_exchange(exchange_id: str):
    return getMoneyExchange(exchange_id)


@app.patch("/users/{user_id}")
async def update_user(user_id: str, user: UpdateUsers = Depends(UsersUp_checker), file: UploadFile or None = None):
    https_url = None
    if file:
        result = cloudinary.uploader.upload(file.file, public_id = user_id)
        url = result.get("url")
        https_url = url[:4] + 's' + url[4:]
    updateDetailUser(user_id,user.dict(exclude_unset = True),https_url)
    return "success, you have updated user info"


@app.patch("/works/{work_id}")
async def update_work(work_id: str, work: UpdateWorks):
    updateDetailWork(work_id,work.dict(exclude_unset = True))
    return "success, you have updated work"


@app.patch("/users/{user_id}/apply/{work_id}")
async def apply_button(user_id: str, work_id: str):
    addUserToListOfCandidate(work_id, user_id)
    addWorkToListOfWork(work_id, user_id)
    initUserStatus(work_id, user_id)
    # notiUserAppToRecruiter()
    

@app.patch("/users/{user_id}/accept/{work_id}")
async def accept_button(user_id: str, work_id: str):
    AcceptButton(user_id, work_id)


@app.patch("/users/{user_id}/appoint/{work_id}/{date}/{time}")
async def appointment_button(user_id: str, work_id: str, date: str, time: str):
    AppointmentButton(user_id, work_id, date, time)


@app.patch("/users/{user_id}/payment/{work_id}")
async def payment_method(work_id: str, user_id: str, review_body: ReviewsRequest):
    addHaveWorkedWith(work_id, user_id)
    manageReview(user_id, work_id, vars(review_body))
    manageMoneyExchange(work_id, user_id)


@app.patch("/users/{user_id}/withdraw/{credit}")
def withdraw_user_credit(user_id: str,credit:int):
    return withdrawUserCredit(user_id,credit)


@app.patch("/users/{user_id}/absent/{work_id}")
async def penalized_user_credit(user_id: str, work_id: str):
    return penalizedUserCredit(user_id, work_id)


@app.patch("/recruiters/{recruiter_id}/topup/{credit}")
def topup_recruiter_credit(recruiter_id: str, credit: int):
    return topupRecruiterCredit(recruiter_id, credit)


@app.delete("/works/{work_id}")
async def delete_work(work_id: str):
   deleteWorkAndListwork(work_id)
   return "success, you have deleted work"
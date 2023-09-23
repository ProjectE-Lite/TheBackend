from database import *
from fastapi import HTTPException
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from userManagement import *
from datetime import timedelta


printer = pprint.PrettyPrinter()


def job_cost_calculator(number_requirement, hourly_income, start_time, end_time):
    start_time = start_time.split(":")
    end_time = end_time.split(":")
    start_f = float(start_time[0] + "." + start_time[1])
    end_f = float(end_time[0] + "." + end_time[1])
    hour_diff = end_f - start_f
    return number_requirement * hourly_income * hour_diff
    

def return_list_items(cursor, name_header):
    res = []
    for item in cursor:
        item["_id"] = str(item["_id"])
        res.append(item)
    return {name_header: res}


def return_items(item, name_header):
    item["_id"] = str(item["_id"])
    return {name_header: item}


def insertPseudoWork(work, recruiter_id):
    work_id = gen_id()
    work["work_id"] = work_id
    work["recruiter_id"] = recruiter_id
    work_date = work["work_date"].split('-')
    end_registeration = datetime(int(work_date[0]), int(work_date[1]), int(work_date[2]), 23, 59, 59)
    end_registeration = end_registeration - timedelta(days = 1)
    end_registeration = str(end_registeration)
    end_registeration = end_registeration.split(" ")
    work["end_registeration"] = end_registeration[0]
    recruiter_credit = RecruitersCollection.find_one({"recruiter_id": recruiter_id})["credit"]
    
    job_cost = job_cost_calculator(work["number_requirement"], work["hourly_income"], work["start_time"], work["end_time"])
    if recruiter_credit < job_cost:
        return "your credit is too low just go to topup"

    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, {"$inc": {"credit": -job_cost}})
    work["pot"] =  job_cost
    work["recruiter_id"] = recruiter_id
    WorksCollection.insert_one(work)
    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, {"$addToSet": {"list_of_work": work_id}})
    matchingFieldOfInterested(work["type_of_work"])
    
    return return_items(work, "work")


def getWorkByWorkDate(work_date):
    ans = []
    work_list = WorksCollection.find({"work_date": work_date})
    for i in work_list:
        ans.append(i["work_id"])
    return {"work_list": ans}


def getWorkByWorkID(work_id):
    item = WorksCollection.find_one({"work_id": work_id})
    if not item:
        raise HTTPException(status_code=400, detail="Work not found")
    return return_items(item, "work")


def getAllWorkInUser(uid: int):
    ans = []
    uinfo = UsersCollection.find_one({"user_id": uid}, {"_id": 0})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    work = uinfo["list_of_work"]
    if not work:
        raise HTTPException(status_code=400, detail="No jobs")
    work_list = WorksCollection.find({"work_id": {"$in": work}}, {"_id": 0})
    for i in work_list:
        ans.append(i["work_id"])
    return {"work_list": ans}


def getWorkDetailsByWorkAndUserId(wid: int, uid: int):
    winfo = WorksCollection.find_one({"work_id": wid}, {"_id": 0})
    if not winfo:
        raise HTTPException(status_code=400, detail="Work not found")
    if str(uid) not in winfo["user_status"]:
        raise HTTPException(status_code=400, detail="User not found")
    sid = winfo["user_status"][str(uid)]
    ans = UserStatusInWorkCollection.find_one({"user_status_id": sid}, {"_id": 0})
    return {"status": ans["user_status"], "work_detail": winfo}


def getUserNotification(uid: int):
    uinfo = UsersCollection.find_one({"user_id": uid}, {"_id": 0})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    noti = uinfo["notification"]
    if not noti:
        raise HTTPException(status_code=400, detail="No notifications")
    ans = list(UsersNotificationCollection.find({"user_noti_id": {"$in": noti}}, {"_id": 0}))
    return ans


def addUserToListOfCandidate(work_id, user_id):
    WorksCollection.update_one({"work_id": work_id}, {"$addToSet": {"list_of_candidate": user_id}})
    

def updateUserStatus(user_status_id, user_status):
    all_updates = {
        "$set": {"user_status": user_status}
    }
    UserStatusInWorkCollection.update_one({"user_status_id": user_status_id}, all_updates)


def updateUserStatusInterview(user_status_id, interview_appointment):
    all_updates = {
        "$set": {"interview_appointment": interview_appointment}
    }
    UserStatusInWorkCollection.update_one({"user_status_id": user_status_id}, all_updates)


def updateUserStatusWorkApp(user_status_id, work_appointment):
    all_updates = {
        "$set": {"work_appointment": work_appointment}
    }
    UserStatusInWorkCollection.update_one({"user_status_id": user_status_id}, all_updates)
    

def initUserStatus(work_id, user_id):
    user_status_id = gen_id()
    
    user_status = {
        "user_status_id": user_status_id,
        "user_status": "waiting",
        "interview_appointment": None,
        "work_appointment": None
    }
    
    UserStatusInWorkCollection.insert_one(user_status)
    temp = str(user_id)
    
    target_dict = {"$set": {f"user_status.{temp}": user_status_id}}
    WorksCollection.update_one({"work_id": work_id}, target_dict)
   

def isEndRegisteration(work_id):
    end_registeration = WorksCollection.find_one({"work_id": work_id})["end_registeration"].split('-')
    
    end_registeration = datetime(int(end_registeration[0]), int(end_registeration[1]), int(end_registeration[2]), 23, 59, 59)

    today = datetime.now()

    if today > end_registeration:
        return True
    else:
        return False


def getWorkStatusAndListOfUser(work_id):
    isEnd = isEndRegisteration(work_id)
    work_cursor = WorksCollection.find_one({"work_id": work_id})
    num_require = work_cursor["number_requirement"]
    
    
    if isEnd != True and num_require != 0:
        status = "still_choosing"
        list_of_candidate = work_cursor["list_of_candidate"]
        return {status: list_of_candidate}

    else:
        status = "choosing_is_completed"
        list_of_worker = work_cursor["list_of_worker"]
        return {status: list_of_worker}


def getUserDetail(user_id):
    uinfo = UsersCollection.find_one({"user_id": user_id}, {"_id": 0})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    return uinfo


def getReviewByPoints(user_id, point):
    uinfo = UsersCollection.find_one({"user_id": user_id}, {"_id": 0})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    if str(point) not in uinfo["feedback"]:
        raise HTTPException(status_code=400, detail="Review not found")
    review = uinfo["feedback"][str(point)]
    ans = list(ReviewsCollection.find({"review_id": {"$in": review}}, {"_id": 0}))
    return ans


def getListOfWorker(work_id):
    winfo = WorksCollection.find_one({"work_id": work_id}, {"_id": 0})
    if not winfo:
        raise HTTPException(status_code=400, detail="Work not found")
    worker = winfo["list_of_worker"]
    return worker


def penalizedUserCredit(user_id):
    penalty = 500
    uinfo = UsersCollection.find_one({"user_id": user_id}, {"_id": 0})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    UsersCollection.update_one({"user_id": user_id},
                               {"$set": {"credit": uinfo["credit"] - penalty}})
    return {"detail": "User has been penalized"}


def AppointmentButton(user_id, work_id, date, time):
    recruiter_id = WorksCollection.find_one({"work_id": work_id})["recruiter_id"]
    recruiter_name = RecruitersCollection.find_one({"recruiter_id": recruiter_id})["name"]
    text = "You have an appointment of interview in " + date + time + " from " + recruiter_name
    user_status_id = WorksCollection.find_one({"work_id": work_id})["user_status"][str(user_id)]
    updateUserStatusInterview(user_status_id, date+time)
    email = "suphanat.wi@ku.th"
    #email = UsersCollection.find_one({"user_id": user_id})["email"]
    EmailNotification(email, "Appointment", text)
    #notiDatabase


def AcceptButton(user_id, work_id):
    all_updates = {
        "$inc": {"number_requirement": -1},
        "$addToSet": {"list_of_worker": user_id}
    }
    WorksCollection.update_one({"work_id": work_id}, all_updates)

    recruiter_id = WorksCollection.find_one({"work_id": work_id})["recruiter_id"]
    recruiter_name = RecruitersCollection.find_one({"recruiter_id": recruiter_id})["name"]
    work_name = WorksCollection.find_one({"work_id": work_id})["name"]
    text = f"{recruiter_name} accepted you to join {work_name}"    
    user_status_id = WorksCollection.find_one({"work_id": work_id})["user_status"][str(user_id)]
    updateUserStatus(user_status_id, "working")
    updateUserStatusWorkApp(user_status_id, "site work details")
    email = "suphanat.wi@ku.th"
    EmailNotification(email, "Accepted", text)


def updateDetailWork(work_id,work):
    work_data = WorksCollection.find_one({"work_id": work_id})
    recruiter_id = work_data["recruiter_id"]
    # ถ้าเปลี่ยนพวกเวลา จำนวนคนรับ ราคา ก็ต้องเปลี่ยนpotด้วย
    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, {"$inc": {"credit": work_data["pot"]}})
    recruiter_credit = RecruitersCollection.find_one({"recruiter_id": recruiter_id})["credit"]    
    job_cost = job_cost_calculator(work["number_requirement"], work["hourly_income"], work["start_time"], work["end_time"])
    if recruiter_credit < job_cost:
        return "can't edit, your credit is too low, need topup"
    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, {"$inc": {"credit": -job_cost}})
    work["pot"] =  job_cost
    WorksCollection.update_one({'work_id':work_id},{'$set':work})
    return 0


def getCandidateOfWork(uid: int):
    listofworker = WorksCollection.find_one({"work_id": uid})
    values = listofworker["list_of_candidate"]
    list=[]
    for i in values:
        namesofid = UsersCollection.find_one({"user_id":i})
        first = namesofid["first_name"]
        last =  namesofid["last_name"]
        tmp=first + " " + last
        list.append(tmp)
    return list
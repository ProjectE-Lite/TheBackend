from database import *
from fastapi import HTTPException
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from userManagement import *
from datetime import timedelta


printer = pprint.PrettyPrinter()

type_work_mapping = {
    "type1": "พนักงานเสิร์ฟ",
    "type2": "พนักงานทำความสะอาด",
    "type3": "ผู้ช่วยเชฟ",
    "type4": "พนักงานต้อนรับ",
    "type5": "พนักงานล้างจาน",
    "type6": "พนักงานส่งอาหาร",
    "type7": "พนักงานช่วยทำความสะอาดโต๊ะ",
    "type8": "พนักงานครัวร้อน"

}





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


def improved_return(item):
    item["_id"] = str(item["_id"])
    return item


def insertPseudoWork(work, recruiter_id):
    rec = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    work["name"] = rec["name"]
    work["recruiter_id"] = recruiter_id
    work_date = work["work_date"].split('-')
    end_registeration = datetime(int(work_date[0]), int(work_date[1]), int(work_date[2]), 23, 59, 59)
    end_registeration = end_registeration - timedelta(days = 1)
    end_registeration = str(end_registeration)
    end_registeration = end_registeration.split(" ")
    work["end_registeration"] = end_registeration[0]
    recruiter_credit = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["credit"]
    
    job_cost = job_cost_calculator(work["number_requirement"], work["hourly_income"], work["start_time"], work["end_time"])
    if recruiter_credit < job_cost:
        return "your credit is too low just go to topup"

    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": -job_cost}})
    work["pot"] =  job_cost
    work["total_worker"] = work["number_requirement"]
    work["image"] = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["image"]
    winfo = WorksCollection.insert_one(work)
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$addToSet": {"list_of_work": str(winfo.inserted_id)}})
    notiFieldOfInterestToUser(work)
    
    return improved_return(work)


def getWorkByWorkDate(work_date):
    ans = []
    work_list = WorksCollection.find({"work_date": work_date})
    for i in work_list:
        ans.append(str(i["_id"]))
    return {"work_list": ans}


def getWorkByWorkID(work_id):
    item = WorksCollection.find_one({"_id": ObjectId(work_id)})
    if not item:
        raise HTTPException(status_code=400, detail="Work not found")
    item["user_status"] = getUserStatusInWork(work_id)
    return improved_return(item)


def getAllWorkInUser(uid: str):
    ans = []
    uinfo = UsersCollection.find_one({"_id": ObjectId(uid)})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    work = uinfo["list_of_work"]
    if not work:
        raise HTTPException(status_code=400, detail="No jobs")
    objwork = [ObjectId(i) for i in work]
    work_list = WorksCollection.find({"_id": {"$in": objwork}})
    for i in work_list:
        ans.append(str(i["_id"]))
    return {"work_list": ans}


def getWorkDetailsByWorkAndUserId(wid: str, uid: str):
    winfo = WorksCollection.find_one({"_id": ObjectId(wid)})
    if not winfo:
        raise HTTPException(status_code=400, detail="Work not found")
    if uid not in winfo["user_status"]:
        raise HTTPException(status_code=400, detail="User not found")
    sid = winfo["user_status"][uid]
    ans = UserStatusInWorkCollection.find_one({"_id": ObjectId(sid)})
    return {"status": ans["user_status"], "work_detail": improved_return(winfo)}


def getAllWorkInRecruiter(rid: str):
    ans = {}
    rinfo = RecruitersCollection.find_one({"_id": ObjectId(rid)})
    if not rinfo:
        raise HTTPException(status_code=400, detail="Recruiter not found")
    work = rinfo["list_of_work"]
    if not work:
        raise HTTPException(status_code=400, detail="No jobs")
    objwork = [ObjectId(i) for i in work]
    work_list = WorksCollection.find({"_id": {"$in": objwork}})
    for i in work_list:
        x = getRecWorkFromListByDate(rid,i["work_date"])
        ans[i["work_date"]] = x
    ordered_ans = sorted(ans.items(), key = lambda x:datetime.strptime(x[0], '%Y-%m-%d'), reverse=True )
    return convert(ordered_ans)


def getUserNotification(uid: str):
    ans = []
    uinfo = UsersCollection.find_one({"_id": ObjectId(uid)})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    noti = uinfo["notification"]
    if not noti:
        raise HTTPException(status_code=400, detail="No notifications")
    objnoti = [ObjectId(i) for i in noti]
    unotilist = UsersNotificationCollection.find({"_id": {"$in": objnoti}})
    for i in unotilist:
        ans.append(str(i["_id"]))
    ans.reverse()
    return ans


def getRecruiterNotification(rid: str):
    ans = []
    rinfo = RecruitersCollection.find_one({"_id": ObjectId(rid)})
    if not rinfo:
        raise HTTPException(status_code=400, detail="Recruiter not found")
    noti = rinfo["notification"]
    if not noti:
        raise HTTPException(status_code=400, detail="No notifications")
    objnoti = [ObjectId(i) for i in noti]
    rnotilist = RecruitersNotificationCollection.find({"_id": {"$in": objnoti}})
    for i in rnotilist:
        ans.append(str(i["_id"]))
    ans.reverse()
    return ans


def getUserNotiDetail(nid: str):
    unoti = UsersNotificationCollection.find_one({"_id": ObjectId(nid)})
    return improved_return(unoti)


def getRecNotiDetail(nid: str):
    rnoti = RecruitersNotificationCollection.find_one({"_id": ObjectId(nid)})
    return improved_return(rnoti)


def addUserToListOfCandidate(work_id, user_id):
    WorksCollection.update_one({"_id": ObjectId(work_id)}, {"$addToSet": {"list_of_candidate": user_id}})
    

def updateUserStatus(user_status_id, user_status):
    all_updates = {
        "$set": {"user_status": user_status}
    }
    UserStatusInWorkCollection.update_one({"_id": ObjectId(user_status_id)}, all_updates)


def updateUserStatusInterview(user_status_id, interview_appointment):
    all_updates = {
        "$set": {"interview_appointment": interview_appointment}
    }
    UserStatusInWorkCollection.update_one({"_id": ObjectId(user_status_id)}, all_updates)


def updateUserStatusWorkApp(user_status_id, work_appointment):
    all_updates = {
        "$set": {"work_appointment": work_appointment}
    }
    UserStatusInWorkCollection.update_one({"_id": ObjectId(user_status_id)}, all_updates)
    

def initUserStatus(work_id, user_id):
    user_status = {
        "user_status": "รอ",
        "interview_appointment": None,
        "work_appointment": None
    }
    
    sinfo = UserStatusInWorkCollection.insert_one(user_status)
    temp = str(user_id)
    
    target_dict = {"$set": {f"user_status.{temp}": str(sinfo.inserted_id)}}
    WorksCollection.update_one({"_id": ObjectId(work_id)}, target_dict)
   

def isEndRegisteration(work_id):
    end_registeration = WorksCollection.find_one({"_id": ObjectId(work_id)})["end_registeration"].split('-')
    
    end_registeration = datetime(int(end_registeration[0]), int(end_registeration[1]), int(end_registeration[2]), 23, 59, 59)

    today = datetime.now()

    if today > end_registeration:
        return True
    else:
        return False


def getWorkStatusAndListOfUser(work_id):
    isEnd = isEndRegisteration(work_id)
    work_cursor = WorksCollection.find_one({"_id": ObjectId(work_id)})
    num_require = work_cursor["number_requirement"]
    
    
    if isEnd != True and num_require != 0:
        status = "still_choosing"
        list_of_candidate = work_cursor["list_of_candidate"]
        return {status: list_of_candidate}

    else:
        status = "choosing_is_completed"
        list_of_worker = work_cursor["list_of_worker"]
        return {status: list_of_worker}


def getUserStatusInWork(work_id):
    ans = {}
    winfo = WorksCollection.find_one({"_id": ObjectId(work_id)})
    ustatus = winfo["user_status"]
    for x,y in ustatus.items():
        ans[x] = getUserStatusDetail(y)
    return ans


def getUserDetail(user_id):
    uinfo = UsersCollection.find_one({"_id": ObjectId(user_id)})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    return improved_return(uinfo)


def getRecruiterDetail(recruiter_id):
    recinfo = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    if not recinfo:
        raise HTTPException(status_code=400, detail="Recruiter not found")
    return improved_return(recinfo)


def getReviewByPoints(user_id, point):
    ans = []
    uinfo = UsersCollection.find_one({"_id": ObjectId(user_id)})
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    if str(point) not in uinfo["feedback"]:
        raise HTTPException(status_code=400, detail="Review not found")
    review = uinfo["feedback"][str(point)]
    objreview = [ObjectId(i) for i in review]
    rlist = ReviewsCollection.find({"_id": {"$in": objreview}})
    for i in rlist:
        ans.append(str(i["_id"]))
    return ans


def getListOfWorker(work_id):
    winfo = WorksCollection.find_one({"_id": ObjectId(work_id)})
    if not winfo:
        raise HTTPException(status_code=400, detail="Work not found")
    worker = winfo["list_of_worker"]
    return worker


def penalizedUserCredit(user_id, work_id):
    penalty = 500
    uinfo = UsersCollection.find_one({"_id": ObjectId(user_id)})
    recruiter_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["recruiter_id"]

    WorksCollection.update_one({"_id": ObjectId(work_id)}, {"$pull": {"list_of_worker": f"{user_id}" }})
    len_list_of_worker = len(WorksCollection.find_one({"_id": ObjectId(work_id)})["list_of_worker"])
    print(len_list_of_worker)
    if len_list_of_worker == 0:
        #returnMoneyFromPotToRecruiter
        money_left_from_pot = WorksCollection.find_one({"_id": ObjectId(work_id)})["pot"]
        RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": money_left_from_pot}})
        
        
    if not uinfo:
        raise HTTPException(status_code=400, detail="User not found")
    UsersCollection.update_one({"_id": ObjectId(user_id)},
                               {"$set": {"credit": uinfo["credit"] - penalty}})
    return {"detail": "User has been penalized"}


def AppointmentButton(user_id, work_id, date, time):
    recruiter_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["recruiter_id"]
    recruiter_name = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["name"]
    recruiter_address = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["address"]
    work_type = WorksCollection.find_one({"_id": ObjectId(work_id)})["type_of_work"]
    
    if work_type in type_work_mapping.keys():
        work_type = type_work_mapping[work_type]
    user_doc = UsersCollection.find_one({"_id": ObjectId(user_id)})
    user_first_name = user_doc["first_name"]
    user_last_name = user_doc["last_name"]

    text = f"""
        สวัสดีคุณ {user_first_name} {user_last_name},

        คุณมีนัดกับ {recruiter_name} เกี่ยวกับ {work_type} ในวันที่ {date} เวลา {time}
        สถานที่ : {recruiter_address}
        โปรดมาให้ถึงก่อนเวลานัดหมาย 15 นาที

        ขอแสดงความนับถือ
        {recruiter_name}
    """

    user_status_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["user_status"][user_id]
    updateUserStatusInterview(user_status_id, date+time)
    #email = "suphanat.wi@ku.th"
    email = UsersCollection.find_one({"_id": ObjectId(user_id)})["email"]
    EmailNotification(email, "Appointment", text)
    #notiDatabase


def AcceptButton(user_id, work_id):
    candidate = WorksCollection.find_one({"_id": ObjectId(work_id)})["list_of_candidate"]
    candidate.remove(user_id)

    all_updates = {
        "$inc": {"number_requirement": -1},
        "$addToSet": {"list_of_worker": user_id},
        "$set": {"list_of_candidate":candidate}
        }
    WorksCollection.update_one({"_id": ObjectId(work_id)}, all_updates)

    recruiter_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["recruiter_id"]
    recruiter_doc = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    user_doc = UsersCollection.find_one({"_id": ObjectId(user_id)})
    user_first_name = user_doc["first_name"]
    user_last_name = user_doc["last_name"]
    recruiter_name = recruiter_doc["name"]
    recruiter_address =recruiter_doc["address"]
    work_doc = WorksCollection.find_one({"_id": ObjectId(work_id)})
    work_type = work_doc["type_of_work"]
    
    if work_type in type_work_mapping.keys():
        work_type = type_work_mapping[work_type]

    
    text = f"""
        สวัสดีคุณ {user_first_name} {user_last_name},

        การยื่นสมัครงานสำหรับ {work_type} ของคุณกับ {recruiter_name} ได้รับการยอมรับแล้ว
        สถานที่ : {recruiter_address}
        โปรดมาให้ถึงที่ทำงานก่อนเวลาทำงาน 30 นาทีเพื่อเตรียมตัวให้พร้อมสำหรับงาน

        ขอแสดงความนับถือ  
        {recruiter_name}


    """    

    
    user_status_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["user_status"][user_id]
    updateUserStatus(user_status_id, "working")
    updateUserStatusWorkApp(user_status_id, recruiter_address)
    email = "suphanat.wi@ku.th"
    EmailNotification(email, "Accepted", text)

def RejectButton(user_id, work_id):
    work = WorksCollection.find_one({"_id": ObjectId(work_id)})
    candidate = work["list_of_candidate"]
    candidate.remove(user_id)
    WorksCollection.update_one({"_id": ObjectId(work_id)}, {"$set": {"list_of_candidate":candidate}})
    user = UsersCollection.find_one({"_id": ObjectId(user_id)})
    tmp = user["list_of_work"]
    tmp.remove(work_id)
    UsersCollection.update_one({"_id": ObjectId(user_id)},{"$set": {"list_of_work": tmp}})

    recruiter = RecruitersCollection.find_one({"_id": ObjectId(work['recruiter_id'])})
    text = f"สวัสดีคุณ {user.first_name},\nการยื่นสมัครงานสำหรับ {work.name} ของคุณถูกปฏิเสธ\nขอแสดงความนับถือ\n{recruiter.name}"
    EmailNotification(user["email"], "Sorry", text)
    
    rc_id = str(recruiter['_id'])         
    x = UsersNotificationCollection.insert_one({'recruiter_id': rc_id ,'date': getNowDate(), 'text': text })
    print(user["_id"])
    UsersCollection.update_one({"_id": ObjectId(user["_id"])}, {"$addToSet": {"notification": str(x.inserted_id)}})
    return 0

def updateDetailUser(user_id,user,url):
    UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$set": user})
    if url:
        UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$set": {"image": url}})


def updateDetailWork(work_id,work):
    work_data = WorksCollection.find_one({"_id": ObjectId(work_id)})
    recruiter_id = work_data["recruiter_id"]
    # ถ้าเปลี่ยนพวกเวลา จำนวนคนรับ ราคา ก็ต้องเปลี่ยนpotด้วย
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": work_data["pot"]}})
    recruiter_credit = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["credit"]    
    job_cost = job_cost_calculator(work["number_requirement"], work["hourly_income"], work["start_time"], work["end_time"])
    if recruiter_credit < job_cost:
        return "can't edit, your credit is too low, need topup"
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": -job_cost}})
    work["pot"] =  job_cost
    work["total_worker"] = work["number_requirement"]
    WorksCollection.update_one({"_id": ObjectId(work_id)}, {"$set": work})


def getCandidateOfWork(uid: str):
    listofworker = WorksCollection.find_one({"_id": ObjectId(uid)})
    values = listofworker["list_of_candidate"]
    list=[]
    for i in values:
        namesofid = UsersCollection.find_one({"_id": ObjectId(i)})
        first = namesofid["first_name"]
        last =  namesofid["last_name"]
        tmp=first + " " + last
        list.append(tmp)
    return list


def deleteWorkAndListwork(work_id):
    work = WorksCollection.find_one({"_id": ObjectId(work_id)})
    recruiter_id =  work["recruiter_id"]
    WorksCollection.delete_one({"_id": ObjectId(work_id)})
    listwork = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["list_of_work"]
    listwork.remove(work_id)
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)},{"$set": {"list_of_work": listwork}})
    list_candidate = work["list_of_candidate"]
    list_worker = work["list_of_worker"]
    list_all_users = list_candidate + list_worker
    for i in list_all_users:
        user = UsersCollection.find_one({"_id": ObjectId(i)})
        tmp = user["list_of_work"]
        tmp.remove(work_id)
        UsersCollection.update_one({"_id": ObjectId(i)},{"$set": {"list_of_work": tmp}})
    return 0


def getRecWorkFromListByDate(recruiter_id,date):
    ans = []
    rinfo = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    work = rinfo["list_of_work"]
    if not work:
        raise HTTPException(status_code=400, detail="No jobs")
    objwork = [ObjectId(i) for i in work]
    work_list = WorksCollection.find({"_id": {"$in": objwork}, "work_date": date})
    for i in work_list:
        ans.append(str(i["_id"]))
    return ans


def getUserStatusDetail(status_id):
    sinfo = UserStatusInWorkCollection.find_one({"_id": ObjectId(status_id)})
    return improved_return(sinfo)


def getMoneyExchange(exchange_id):
    minfo = MoneyExchangeCollection.find_one({"_id": ObjectId(exchange_id)})
    return improved_return(minfo)


def getReviewDetail(review_id):
    revinfo = ReviewsCollection.find_one({"_id": ObjectId(review_id)})
    rinfo = RecruitersCollection.find_one({"_id": ObjectId(revinfo["recruiter_id"])})
    ans = improved_return(revinfo)
    ans["recruiter_name"] = rinfo["name"]
    ans["recruiter_image"] = rinfo["image"]
    return ans


#delete particular element in array
#RecruitersCollection.update_one({"_id": ObjectId("6519dbdd761718fdedbe45b1")}, {"$pull": {"list_of_work": "item2" }})
   
def notiFieldOfInterestToUser(work):
   users = UsersCollection.find()
   for user in users:
        try:
            if user['field_of_interested'][work['type_of_work']]:
                text = work["name"] + '(งานแนะนำ) : วันที่ '+ work["work_date"]

                work_type = work["type_of_work"]
                if work_type in type_work_mapping.keys():
                    work_type = type_work_mapping[work_type]
                recruiter_id = work["recruiter_id"]
                recruiter_name = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["name"]
                    
                text = f"""
                    สวัสดีคุณ {user["first_name"]} {user["last_name"]},

                    จากความสนใจที่คุณได้กรอกมา ตอนนี้งานที่ตรงกับความสนใจของคุณถูกประกาศมาแล้ว
                    ประเภทงาน : {work_type}
                    ชื่อผู้ประกอบการ: {recruiter_name}
                    คุณสามารถกดสมัครงานนี้ได้แล้ว

                    ขอแสดงความนับถือ
                    {recruiter_name}
                """
                recruiter = RecruitersCollection.find_one({"_id": ObjectId(work['recruiter_id'])})
                rc_id = str(recruiter['_id'])         
                x = UsersNotificationCollection.insert_one({'recruiter_id': rc_id ,'date': work["work_date"], 'text': text })
                
                EmailNotification(user["email"], "you may interest this job", text)
                print(user["_id"])
                UsersCollection.update_one({"_id": ObjectId(user["_id"])}, {"$addToSet": {"notification": str(x.inserted_id)}})
                
        except KeyError:
            print(f"{work['type_of_work']} is unknown.")
            #except for user who don't have FieldOfInterest
   return 0




def notiUserAppToRecruiter(work_id, user_id):
    recruiter_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["recruiter_id"]
    recruiter_doc = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    recruiter_email = recruiter_doc["email"]
    recruiter_name = recruiter_doc["name"]
    work_doc = WorksCollection.find_one({"_id": ObjectId(work_id)})
    work_type = work_doc["type_of_work"]

    user_doc = UsersCollection.find_one({"_id": ObjectId(user_id)})
    if work_type in type_work_mapping.keys():
        work_type = type_work_mapping[work_type]
    
    text = f"""
        สวัสดีคุณ {recruiter_name},

        งาน {work_type} ของคุณมีผู้สมัครใหม่ชื่อ {user_doc["first_name"]} {user_doc["last_name"]} มาเพิ่มแล้ว
        กรุณากดตอบรับ/ปฏิเสธ

        ขอแสดงความนับถือ
        E-lite
    """
    EmailNotification(recruiter_email, "มีผู้สมัครเข้ามาในงานของคุณ", text)
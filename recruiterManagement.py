from database import *
from bson.objectid import ObjectId
import pprint
from datetime import datetime
from helpingFunction import *


def insertPseudoRecruiter(recruiter):
    rinfo = RecruitersCollection.insert_one(recruiter)
    return rinfo.inserted_id


def check_recruiter(uname: str, passwd: str):
    rinfo = RecruitersCollection.find_one({"username": uname, "password": passwd})
    if not rinfo:
        return 0
    else:
        return rinfo
    

#can recruiters add type_of_work?




def getRecListOfMoneyExchange(rid: str):
    ans = []
    mid = RecruitersCollection.find_one({"_id": ObjectId(rid)})["list_of_money_exchange"]
    objmid = [ObjectId(i) for i in mid]
    mlist = MoneyExchangeCollection.find({"_id": {"$in": objmid}})
    for i in mlist:
        ans.append(str(i["_id"]))
    ans.reverse()
    return ans


def addHaveWorkedWith(work_id, user_id):
    work_cursor = WorksCollection.find_one({"_id": ObjectId(work_id)})
    work_type = work_cursor["type_of_work"]
    recruiter_id = work_cursor["recruiter_id"]
    print(work_type, recruiter_id)

    all_updates = {
        "$set" : {f"have_worked_with.{work_type}.{ObjectId(user_id)}": True}
    }
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, all_updates)


def topupRecruiterCredit(recruiter_id, credit):
    datenow = datetime.now()
    money_exchange_body = {"from": "Bank",
                           "to": recruiter_id,
                           "date": datenow,
                           "credit": credit}
    mid = MoneyExchangeCollection.insert_one(money_exchange_body)
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$addToSet": {"list_of_money_exchange": str(mid.inserted_id)}})
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": credit}})
    return {"detail": f"Added {credit} credit to {recruiter_id}"}

def checkHaveWorkedWith(recruiter_id: str, user_id: str):
    temp = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})["have_worked_with"]
    for k, v in temp.items():
        for user in v.keys():
            if user_id == user:
                #user_name = UsersCollection.find_one({"_id": ObjectId(user_id)})["name"]
                recruiter_name = UsersCollection.find_one({"_id": ObjectId(recruiter_id)})["name"]
                return f"เคยทำงานกับ {recruiter_name} ประเภท {k}"
    
    #user_name = UsersCollection.find_one({"_id": ObjectId(user_id)})["name"]
    recruiter_name = UsersCollection.find_one({"_id": ObjectId(recruiter_id)})["name"]
    return f"ไม่เคยทำงานกับ {recruiter_name}"


#d
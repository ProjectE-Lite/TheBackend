from database import *
from bson.objectid import ObjectId
import pprint
from datetime import datetime
from helpingFunction import *


def insertPseudoRecruiter(recruiter):
    RecruitersCollection.insert_one(recruiter)


def check_recruiter(uname: str, passwd: str):
    rinfo = RecruitersCollection.find_one({"username": uname, "password": passwd})
    if not rinfo:
        return 0
    else:
        return rinfo
    

#can recruiters add type_of_work?




def addHaveWorkedWith(work_id, user_id):
    work_cursor = WorksCollection.find_one({"_id": ObjectId(work_id)})
    work_type = work_cursor["type_of_work"]
    recruiter_id = work_cursor["_id"]

    all_updates = {
        "$set" : {f"have_worked_with.{work_type}.{user_id}": True}
    }


    RecruitersCollection.update_one({"_id": recruiter_id}, all_updates)




from database import *
from bson.objectid import ObjectId
import pprint
from datetime import datetime
from helpingFunction import *


def insertPseudoRecruiter(recruiter):
    recruiter_id = gen_id()
    recruiter["recruiter_id"] = recruiter_id
    RecruitersCollection.insert_one(recruiter)
    

#can recruiters add type_of_work?


def addHaveWorkedWith(recruiter_id, work_type, user_id):
    
    all_updates = {
        "$set" : {f"have_worked_with.{work_type}.{user_id}": True}
    }

    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, all_updates)
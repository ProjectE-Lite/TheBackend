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








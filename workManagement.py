import pymongo
from bson.objectid import ObjectId
import pprint
from id_generator import *
from helpingFunction import *
from userManagement import *



printer = pprint.PrettyPrinter()

connection_string = "mongodb+srv://radnha:radnha2435@softenproject-database.ochwdfb.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(connection_string)

WorksCollection = client["NineTest"]["Works"]
RecruitersCollection = client["NineTest"]["Recruiters"]
UserStatusInWorkCollection = client["NineTest"]["UserStatusInWork"]


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
    
    return "you have created work"


def getWorkByWorkDate(work_date):
    work_list = WorksCollection.find({"work_date": work_date})
    return return_list_items(work_list, "work_list")



def getWorkByWorkID(work_id):
    item = WorksCollection.find_one({"work_id": work_id})
    return return_items(item, "work")


def addUserToListOfCandidate(work_id, user_id):
    WorksCollection.update_one({"work_id": work_id}, {"$addToSet": {"list_of_candidate": user_id}})
    


def updateUserStatus(user_status_id, user_status, interview_appointment, work_appointment):
    all_updates = {
        "$set": {"user_status": user_status,
                 "interview_appointment": interview_appointment,
                 "work_appointment": work_appointment}
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



    
    



def manageUserInWork(work_id):
    isEnd = isEndRegisteration(work_id)
    work_cursor = WorksCollection.find_one({"work_id": work_id})
    num_require = work_cursor["number_requirement"]
    
    
    if isEnd != True and num_require != 0:
        status = "still_choosing"
        list_of_candidate = work_cursor["list_of_candidiate"]
        return {status: list_of_candidate}

    else:
        status = "choosing_is_completed"
        list_of_worker = work_cursor["list_of_worker"]
        return {status: list_of_worker}

    
print(manageUserInWork(3))

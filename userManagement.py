from database import *
from bson.objectid import ObjectId
import pprint
from helpingFunction import *


printer = pprint.PrettyPrinter()


def insertPseudoUser(user):
    user_id = gen_id()
    user["user_id"] = user_id
    UsersCollection.insert_one(user)


def check_user(uname: str, passwd: str):
    uinfo = UsersCollection.find_one({"username": uname, "password": passwd}, {"_id": 0})
    if not uinfo:
        return 0
    else:
        return uinfo
    

def addWorkToListOfWork(work_id, user_id):
    UsersCollection.update_one({"user_id": user_id}, {"$addToSet": {"list_of_work": work_id}})


def matchingFieldOfInterested(type_of_work):
    users_cursor = UsersCollection.find({f"field_of_interested.{type_of_work}": True})
    for item in users_cursor:
        print("worktype matching with user: ",item["user_id"])
        #notiToUser(item["user_id"])









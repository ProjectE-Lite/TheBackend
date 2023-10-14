from database import *
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from datetime import datetime,timedelta


printer = pprint.PrettyPrinter()


def insertPseudoUser(user):
    uinfo = UsersCollection.insert_one(user)
    UsersCollection.update_one({"_id": uinfo.inserted_id}, {"$set": {"image": "https://res.cloudinary.com/dig1qtfkr/image/upload/v1696069288/default_profile.jpg"}})


def check_user(uname: str, passwd: str):
    uinfo = UsersCollection.find_one({"username": uname, "password": passwd})
    if not uinfo:
        return 0
    else:
        return uinfo
    

def addWorkToListOfWork(work_id, user_id):
    UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"list_of_work": work_id}})


def matchingFieldOfInterested(type_of_work):
    users_cursor = UsersCollection.find({f"field_of_interested.{type_of_work}": True})
    for item in users_cursor:
        print("worktype matching with user: ",str(item["_id"]))
        #notiToUser(item["user_id"])


def getUserListOfMoneyExchange(uid: str):
    ans = []
    mid = UsersCollection.find_one({"_id": ObjectId(uid)})["list_of_money_exchange"]
    objmid = [ObjectId(i) for i in mid]
    mlist = MoneyExchangeCollection.find({"_id": {"$in": objmid}})
    for i in mlist:
        ans.append(str(i["_id"]))
    ans.reverse()
    return ans


def withdrawUserCredit(uid: str,credit: int):    
    datenow = datetime.now()
    money_exchange_body = {"from": uid,
                           "to": "Bank",
                           "date": datenow,
                           "credit": -credit}
    mid = MoneyExchangeCollection.insert_one(money_exchange_body)
    UsersCollection.update_one({"_id": ObjectId(uid)}, {"$addToSet": {"list_of_money_exchange": str(mid.inserted_id)}})
    
    userlist=UsersCollection.find_one({"_id":ObjectId(uid)})
    values = userlist["credit"]
    values=values-credit
    txt_update={"$set":{
                            "credit" : values,
                        }
                }
    UsersCollection.update_one({"_id":ObjectId(uid)},txt_update)
    
    return {"details": f"Tranferred {credit} credit to Bank", "account_credit": values}



def updateFieldOfInterested(uid: str, fieldint_body):

    UsersCollection.update_one({"_id": ObjectId(uid)}, {"$set": {"field_of_interested": fieldint_body}})
    return f"updated field of interested to {uid}"



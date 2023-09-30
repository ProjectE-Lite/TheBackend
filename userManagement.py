from database import *
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from datetime import datetime,timedelta


printer = pprint.PrettyPrinter()


def insertPseudoUser(user):
    uinfo = UsersCollection.insert_one(user)
    UsersCollection.update_one({"_id": uinfo.inserted_id}, {"$set": {"image": "http://res.cloudinary.com/dig1qtfkr/image/upload/v1696069288/default_profile.jpg"}})


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
    moneylist=MoneyExchangeCollection.find_one({"_id": ObjectId(uid)})
    values = moneylist["total_credit"]
    values = str(values)
    list_of_money=moneylist["list_of_money_exchange"]
    dict={}
    list=[list_of_money]
    dict[values]=list
    return dict


def withdrawUserCredit(uid: str,credit: int):    
    tmp = str(datetime.now())[:-3]
    charinsert="+00:00"
    mod_tmp=tmp+charinsert
    charfind=" "
    charinsert="T"
    indexfind=tmp.find(charfind)
    timestr=mod_tmp[:indexfind]+charinsert+mod_tmp[indexfind+1:]
    txt={
        "from": uid,
        "to": "Bank",
        "date":timestr,
        "credit": credit,
                }
    MoneyExchangeCollection.insert_one(txt)
    findmoneyex=MoneyExchangeCollection.find_one(txt)
    UsersCollection.update_one({"_id": ObjectId(uid)}, {"$addToSet": {"list_of_money_exchange": str(findmoneyex["_id"])}})
    
    userlist=UsersCollection.find_one({"_id":ObjectId(uid)})
    values = userlist["credit"]
    values=values-credit
    txt_update={"$set":{
                            "credit" : values,
                        }
                }
    UsersCollection.update_one({"_id":ObjectId(uid)},txt_update)
    
    return {"details": f"Tranfer to Bank {values}"}
from database import *
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from datetime import datetime,timedelta


printer = pprint.PrettyPrinter()


def insertPseudoUser(user):
    UsersCollection.insert_one(user)


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


#์ALERT NEED FIXING
def withdrawUserCredit(uid: int,wid: int):
    moneylist=MoneyExchangeCollection.find_one({"_id":uid})
    values = moneylist["total_credit"]

    values=values-wid
    tmp=str(datetime.now()-timedelta(hours=7))
    charfind="."
    charinsert="+07:00"
    indexfind=tmp.find(charfind)
    mod_tmp=tmp[:indexfind]+charinsert
    charfind=" "
    charinsert="T"
    indexfind=tmp.find(charfind)
    mod_tmp=mod_tmp[:indexfind]+charinsert+mod_tmp[indexfind+1:]
        
    txt_update={"$set":{
                            "total_credit" : values,
                        },
                "$push":{
                    "list_of_money_exchange":[mod_tmp,-wid]
                }
                }
    MoneyExchangeCollection.update_one({"_id":uid},txt_update)
    
    userlist=UsersCollection.find_one({"_id":uid})
    values = userlist["credit"]
    values=values-wid
    txt_update={"$set":{
                            "credit" : values,
                        }
                }
    UsersCollection.update_one({"_id":uid},txt_update)
    return {"details": f"Tranfer to Bank {values}"}
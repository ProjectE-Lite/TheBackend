from database import *
from bson.objectid import ObjectId
import pprint
from helpingFunction import *
from datetime import datetime,timedelta

printer = pprint.PrettyPrinter()

def getMoneyExchange(exchange_id):
    minfo = MoneyExchangeCollection.find_one({"_id": ObjectId(exchange_id)})
    return improved_return(minfo)

def improved_return(item):
    item["_id"] = str(item["_id"])
    return item

def insertPseudoUser(user):
    uinfo = UsersCollection.insert_one(user)
    UsersCollection.update_one({"_id": uinfo.inserted_id}, {"$set": {"image": "https://res.cloudinary.com/dig1qtfkr/image/upload/v1696069288/default_profile.jpg"}})


def check_user(uname: str, passwd: str):
    uinfo = UsersCollection.find_one({"username": uname, "password": passwd})
    if not uinfo:
        return 0
    else:
        return uinfo
    

def userForgotPassword(uname: str):
    uinfo = UsersCollection.find_one({"username": uname})
    if not uinfo:
        raise HTTPException(status_code=400, detail="There's no account with that username")
    body = f"""
        สวัสดีคุณ {uinfo["first_name"]} {uinfo["last_name"]},

        รหัสผ่านของคุณคือ
        {uinfo["password"]}

        ขอแสดงความนับถือ
        E-Lite
    """
    EmailNotification(uinfo["email"], "รหัสผ่านของคุณ", body)
    return {"detail": "Your password has been sent to your email address."}
    

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

def getUserMoneyExchangeMonthly(uid: str, month:str):
    inn = 0 
    out = 0
    for i in getUserListOfMoneyExchange(uid):
        x = getMoneyExchange(i)
        m = x["date"].month
        y = x["date"].year
        cerrent_year = datetime.now().year
        credit = int(x["credit"])
        print(y)
        if str(m)==month and y == cerrent_year :
            if credit >= 0 :
                inn+=credit
            else:
                out+=credit
    return {"in": inn ,"out": out*-1}

def getUserMoneyMonthly(uid: str):
    result = []
    ans = []
    month = []
    for i in getUserListOfMoneyExchange(uid):
        x = getMoneyExchange(i)
        m = x["date"].month
        if m not in month:
            month.append(m)
    for m in month:
        ans.append(str(m))
        ans.append(getUserMoneyExchangeMonthly(uid, str(m)))
        result.append(ans)
        ans = []
    return result


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
    
    usernoti_body = {}
    nowdate = getNowDate()
    usernoti_body["date"] = nowdate[0]+'-'+nowdate[1]+'-'+nowdate[2]
    usernoti_body["recruiter_id"] = 0
    usernoti_body["text"] = f"ท่านได้ถอนเงินจำนวณ {credit} ออกจากระบบ"

    return {"details": f"Tranferred {credit} credit to Bank", "account_credit": values}



def updateFieldOfInterested(uid: str, fieldint_body):

    UsersCollection.update_one({"_id": ObjectId(uid)}, {"$set": {"field_of_interested": fieldint_body}})
    return f"updated field of interested to {uid}"



from bson.objectid import ObjectId
import datetime
from datetime import datetime, timedelta
import pprint
from database import *
from model import *
from fastapi import Form, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import ValidationError



models = {"recruiters": Recruiters, "users": Users, "works": Works, "reviews": Reviews,
          "recruitersReq": RecruitersRequest, "usersReq": UsersRequest, "worksReq": WorksRequest, "reviewsReq": ReviewsRequest,
          "login": Login, "usersUp": UpdateUsers, "worksUp": UpdateWorks}


class DataChecker:
    def __init__(self, name: str):
        self.name = name

    def __call__(self, data: str = Form(...)):
        try:
            model = models[self.name].parse_raw(data)
        except ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return model


def return_items(item, name_header):
    return {name_header: item}


def getNowDate():
    today = datetime.now()
    x = str(today).split(' ') 
    date_of_today = x[0].split('-')
    return date_of_today


def getNowTime():
    today = datetime.now()
    x = str(today).split(' ') 
    date_of_today = x[1].split('-')
    return date_of_today


def getNowDayName():
    today = datetime.now()
    day_name = today.strftime('%A')
    return day_name


def genNext12Days():
    date_of_today = getNowDate()
    start = datetime(int(date_of_today[0]), int(date_of_today[1]), int(date_of_today[2]))
    K = 13
    res = []
    for day in range(K):
        date = (start + timedelta(days = day)).isoformat()
        date = date.split('T')[0].split('-')
        qq = datetime(int(date[0]), int(date[1]), int(date[2]))
        ddate = str(date[0]) + '-' + str(date[1]) + '-' + str(date[2])
        day_name = qq.strftime('%A')
        temp = [ddate, day_name]
        res.append(temp)
    res = res[1:]
    return return_items(res, "next12Days")
        

def EmailNotification(email_receiver, subject, body):
    
    from email.message import EmailMessage
    import ssl
    import smtplib
    
    email_sender = "owen0867950578@gmail.com"
    email_password = "sxvdwivteicovsxu"
    
    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_receiver
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_receiver, em.as_string())


def job_cost_calculator(number_requirement, hourly_income, start_time, end_time):
    start_time = start_time.split(":")
    end_time = end_time.split(":")
    start_f = float(start_time[0] + "." + start_time[1])
    end_f = float(end_time[0] + "." + end_time[1])
    hour_diff = end_f - start_f
    return number_requirement * hourly_income * hour_diff


def cost_per_person(hourly_income, start_time, end_time):
    start_time = start_time.split(":")
    end_time = end_time.split(":")
    start_f = float(start_time[0] + "." + start_time[1])
    end_f = float(end_time[0] + "." + end_time[1])
    hour_diff = end_f - start_f
    return hourly_income * hour_diff
    

def insertMoneyExchange(recruiter_id, user_id, cost):
    datenow = datetime.now()
    money_exchange_body = {"from": recruiter_id,
                           "to": user_id,
                           "date": datenow,
                           "credit": cost}
    
    minfo = MoneyExchangeCollection.insert_one(money_exchange_body)
    RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$addToSet": {"list_of_money_exchange": str(minfo.inserted_id)}})
    UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$addToSet": {"list_of_money_exchange": str(minfo.inserted_id)}})


def isEndWorkProcess(work_id: str):
    list_of_user_status_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["user_status"].values()
    
    for id in list_of_user_status_id:
        status = UserStatusInWorkCollection.find_one({"_id": ObjectId(id)})["user_status"]
        if status == "working":
            return False
    return True
    

def manageMoneyExchange(work_id, user_id):
    workdoc = WorksCollection.find_one({"_id": ObjectId(work_id)})    
    cost = cost_per_person(workdoc["hourly_income"], workdoc["start_time"], workdoc["end_time"])
    
    #pot -= cost
    WorksCollection.update_one({"_id": ObjectId(work_id)}, {"$inc": {"pot": -cost}})
    #user.credit += cost
    UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$inc": {"credit": cost}})

    # deal with MoneyExchange Database
    recruiter_id = workdoc["recruiter_id"]
    insertMoneyExchange(recruiter_id, user_id, cost)

    recruiterdoc = RecruitersCollection.find_one({"_id": ObjectId(recruiter_id)})
    userdoc = UsersCollection.find_one({"_id": ObjectId(user_id)})
    
    recruiter_name = recruiterdoc["name"]
   
    
    #update status section
    user_stat_id = workdoc["user_status"][user_id]
    UserStatusInWorkCollection.update_one({"_id": ObjectId(user_stat_id)}, {"$set": {"user_status": "paid"}})



    ####################### if there is no working -> return money from pot to recruiter -> end process of work
    is_end_work_process = isEndWorkProcess(work_id)
    if is_end_work_process:
        #return money from pot to recruiter
        money_left_from_pot = WorksCollection.find_one({"_id": ObjectId(work_id)})["pot"]
        RecruitersCollection.update_one({"_id": ObjectId(recruiter_id)}, {"$inc": {"credit": money_left_from_pot}})
     
    
    
    subject = "คุณได้รับค่าจ้าง"
    #body = f"{recruiter_name} has paid you {cost} for {work_name}"
    body = f"""
        สวัสดีคุณ {userdoc["first_name"]} {userdoc["last_name"]},

        ยินดีด้วย
        คุณได้รับค่าจ้างจำนวน {cost} บาทแล้วจาก {recruiter_name} 

        ขอแสดงความนับถือ      
        {recruiter_name}

    """
    usernoti_body = {}
    usernoti_body["recruiter_id"] = str(recruiter_id)
    nowdate = getNowDate()
    usernoti_body["date"] = nowdate[0] + '-' + nowdate[1] + '-' + nowdate[2]
    usernoti_body["text"] = body
    UsersNotificationCollection.insert_one(usernoti_body)
    
    
    EmailNotification(userdoc["email"], subject, body)
    

def manageReview(user_id, work_id, review_body):
    recruiter_id = WorksCollection.find_one({"_id": ObjectId(work_id)})["recruiter_id"]
    score = review_body["score"]
    text = review_body["text"]
    
    review_doc = {"recruiter_id": recruiter_id,
                  "score": score,
                  "text": text}
    
    rinfo = ReviewsCollection.insert_one(review_doc)

    all_updates = {
        "$addToSet": {f"feedback.{score}": str(rinfo.inserted_id)}
    }
    UsersCollection.update_one({"_id": ObjectId(user_id)}, all_updates)
    managePoint(user_id)


def managePoint(user_id):
    uinfo = UsersCollection.find_one({"_id": ObjectId(user_id)})
    totalpoint = 0
    count = 0
    if uinfo["feedback"]:
        for x,y in uinfo["feedback"].items():
            count += len(y)
            totalpoint += int(x)*len(y)
        avgpoint = totalpoint / count
    else:
        avgpoint = 0
    UsersCollection.update_one({"_id": ObjectId(user_id)}, {"$set": {"point": avgpoint}})


def convert(lst):
   res_dict = {}
   for i in range(len(lst)):
       res_dict[lst[i][0]] = lst[i][1]
   return res_dict
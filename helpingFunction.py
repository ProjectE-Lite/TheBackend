import datetime
from datetime import datetime, timedelta
import pprint
from database import *


base_id = 0

def gen_id():
    global base_id
    base_id += 1
    return base_id

def reset_id():
    global base_id
    base_id = 0


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
    money_exchange_id = gen_id()
    money_exchange_body = {"money_exchange_id": money_exchange_id,
                           "from": recruiter_id,
                           "to": user_id,
                           "date": datenow,
                           "credit": cost}
    
    MoneyExchangeCollection.insert_one(money_exchange_body)
    RecruitersCollection.update_one({"recruiter_id": recruiter_id}, {"$addToSet": {"list_of_money_exchange": money_exchange_id}})
    UsersCollection.update_one({"user_id": user_id}, {"$addToSet": {"list_of_money_exchange": money_exchange_id}})



def manageMoneyExchange(work_id, user_id):
    workdoc = WorksCollection.find_one({"work_id": work_id})    
    cost = cost_per_person(workdoc["hourly_income"], workdoc["start_time"], workdoc["end_time"])
    
    #pot -= cost
    WorksCollection.update_one({"work_id": work_id}, {"$inc": {"pot": -cost}})
    #user.credit += cost
    UsersCollection.update_one({"user_id": user_id}, {"$inc": {"credit": cost}})

    # deal with MoneyExchange Database
    recruiter_id = workdoc["recruiter_id"]
    insertMoneyExchange(recruiter_id, user_id, cost)

    recruiterdoc = RecruitersCollection.find_one({"recruiter_id": recruiter_id})
    userdoc = UsersCollection.find_one({"user_id": user_id})
    
    recruiter_name = recruiterdoc["name"]
    work_name = workdoc["name"]

    subject = "brooo you have got a moneyyyy"
    body = f"{recruiter_name} has paid you {cost} for {work_name}"
    EmailNotification(userdoc["email"], subject, body)
    

def manageReview(user_id, work_id, review_body):
    
    
    recruiter_id = WorksCollection.find_one({"work_id": work_id})["recruiter_id"]
    score = review_body["score"]
    text = review_body["text"]
    
    review_id = gen_id()
    
    review_doc = {"review_id": review_id,
                  "recruiter_id": recruiter_id,
                  "score": score,
                  "text": text}
    
    ReviewsCollection.insert_one(review_doc)

    all_updates = {
        "$addToSet": {f"feedback.{score}": review_id}
    }
    UsersCollection.update_one({"user_id":user_id}, all_updates)


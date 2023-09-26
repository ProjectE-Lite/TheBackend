from pymongo import MongoClient


client = MongoClient(
    "mongodb+srv://radnha:radnha2435@softenproject-database.ochwdfb.mongodb.net/?retryWrites=true&w=majority"
)


collection = client["E-lite"]
UsersCollection = collection["Users"]
RecruitersCollection = collection["Recruiters"]
WorksCollection = collection["Works"]
UserStatusInWorkCollection = collection["UserStatusInWork"]
UsersNotificationCollection = collection["UsersNotification"]
RecruitersNotificationCollection = collection["RecruitersNotification"]
ReviewsCollection = collection["Reviews"]
MoneyExchangeCollection = collection["MoneyExchange"]
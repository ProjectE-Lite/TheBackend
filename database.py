import os
from pymongo import MongoClient
from dotenv import load_dotenv
import cloudinary


load_dotenv(".env")
mongouser = os.getenv("MONGO_USERNAME")
mongopass = os.getenv("MONGO_PASSWORD")
cloudname = os.getenv("CLOUD_NAME")
apikey = os.getenv("API_KEY")
apisecret = os.getenv("API_SECRET")

client = MongoClient(
    f"mongodb+srv://{mongouser}:{mongopass}@softenproject-database.ochwdfb.mongodb.net/?retryWrites=true&w=majority"
)

cloudinary.config(
    cloud_name = cloudname,
    api_key = apikey,
    api_secret = apisecret
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
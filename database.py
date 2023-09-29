from pymongo import MongoClient
from decouple import config
import cloudinary


mongouser = config("MONGO_USERNAME")
mongopass = config("MONGO_PASSWORD")
cloudname = config("CLOUD_NAME")
apikey = config("API_KEY")
apisecret = config("API_SECRET")

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
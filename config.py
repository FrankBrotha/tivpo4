import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://airbnbsuperuser:mycoolpassword123@postgres/airbnb'
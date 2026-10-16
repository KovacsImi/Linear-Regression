import kagglehub
import os

kaggle_api_key = os.environ['JAVA_EMAIL_PASSWORD'] 

print(kaggle_api_key)

kagglehub.login(kaggle_api_key)
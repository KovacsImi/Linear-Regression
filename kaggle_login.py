import kagglehub
import os

kaggle_api_key = os.environ['kaggle_api_key'] 

print(kaggle_api_key)

kagglehub.login(kaggle_api_key)
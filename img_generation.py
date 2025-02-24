from dotenv import load_dotenv
import os

load_dotenv()  # Load .env variables

API_KEY = os.getenv("DEEPAI_API_KEY")

print(API_KEY)
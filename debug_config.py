from config import Config
import os

print(f"CWD: {os.getcwd()}")
print(f"DATABASE_URL env: {os.environ.get('DATABASE_URL')}")
print(f"Config URI: {Config.SQLALCHEMY_DATABASE_URI}")

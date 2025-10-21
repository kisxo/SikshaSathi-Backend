import logging
from app.db.database import engine, create_db_and_tables
from sqlalchemy import text
import os
from app.db.models import (
    admin_model,
    anganwadi_model,
    beneficiary_model,
    daily_tracking_model,
    officer_model,
    ration_model,
    staff_attendance_model,
    staff_model,
    student_attendance_model,
    student_model,
)
logger = logging.getLogger('uvicorn.error')

# Function to run during server start up.
# To initialize and check various components required by the application.
# Raises error if any function fails.
def startup():
    logger.info("\n")
    logger.info("Start up check for Fastapi Gym Management\n")
    check_db_connection()
    init_database_models()
    create_media_folders()

def check_db_connection():
    logger.info("Starting Database")
    logger.info("Connecting to database.....")
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connected successfully!\n")
    except Exception as e:
        logger.error("Database connection failed!\n")
        raise e

def init_database_models():
    logger.info("Initializing Database Models.....")
    try:
        create_db_and_tables()
        logger.info("Database Models initialization successfully!\n")
    except Exception as e:
        logger.error("Database Models initialization failed!\n")
        raise e

def create_media_folders():
    logger.info("Verifying media folder and creating if does not exists.....\n")
    try:
        os.makedirs('media', exist_ok=True)
        os.makedirs('media/images/staffs', exist_ok=True)
        os.makedirs('media/images/students', exist_ok=True)
        logger.info("Media initialized successfully !\n")
    except Exception as e:
        logger.error("Media folder initialization failed !\n")
        raise e
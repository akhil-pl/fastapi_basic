import os
import logging

def configure_logging():
    log_folder = "log"  # Name of the log folder

    # Create the log folder if it doesn't exist
    os.makedirs(log_folder, exist_ok=True)

    log_file_path = os.path.join(log_folder, "app.log")

    logging.basicConfig(filename=log_file_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def error_middleware(request, call_next):
    try:
        response = call_next(request)
        return response
    except Exception as e:
        logging.error(f"An error occurred while processing request: {e}")
        raise

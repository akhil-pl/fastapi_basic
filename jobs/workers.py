from celery import Celery
from fastapi import FastAPI, Depends

app = FastAPI()

celery = Celery('tasks', broker='redis://localhost:6379')

# Create a subclass of the Task,  that wraps the task execution in an application context.
# class ContextTask(celery.Task):
#     def __call__(self, *args, **kwargs):
#         with app.app_context():
#             # return self.run(*args, **kwargs)
#             return super().__call__(*args, **kwargs)
        

# Use the ContextTask as the base for your Celery tasks
# celery.Task = ContextTask
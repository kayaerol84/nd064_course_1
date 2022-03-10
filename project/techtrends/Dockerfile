FROM python:3.8
LABEL maintainer="Erol Shaban"

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
RUN python init_db.py

# command to run on container start
CMD [ "python", "app.py" ]

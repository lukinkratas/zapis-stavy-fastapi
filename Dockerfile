FROM python:3.11.0

# set the working directory
WORKDIR /api

# install dependencies
# COPY ./requirements.txt /api
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# copy the scripts to the folder
COPY . /api

# start the server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]

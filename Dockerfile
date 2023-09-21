FROM python:3.8-slim-buster
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt

# TODO: Run the sudo update command and AWS-cli install command
# RUN apt-get update && apt-get install -y sudo
CMD ["python", "app.py"]
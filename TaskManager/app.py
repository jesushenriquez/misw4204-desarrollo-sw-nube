import datetime

from flask import Flask, request
import requests
from celery import Celery
import time

celery_app = Celery("informacionHvBuscadores", broker="redis://redis:6379/0")

app = Flask(__name__)

MATCHING_SERVICE_URL = "http://motor-emparejamiento:6000/matching"
CIRCUIT_BREAKER_STATE = "closed"


@app.route("/")
def hello():
    return "Hello from informacionHvBuscadores!"


@app.route("/getInformacionBuscador", methods=["GET"])
def getInformacionBuscardo():
    candidate_json = {
        "name": "John Smith",
        "email": "john.smith@example.com",
        "phone": "+1 (123) 456-7890",
        "linkedin": "https://www.linkedin.com/in/johnsmith",
        "github": "https://github.com/johnsmith",
        "summary": "Experienced software developer with a passion for creating efficient and scalable solutions. Strong background in web development and a love for problem-solving.",
        "skills": [
            "JavaScript"
        ],
        "experience": [
            {
                "position": "Senior Software Engineer",
                "company": "TechCo Inc.",
                "location": "San Francisco, CA",
                "startDate": "January 2018",
                "endDate": "Present",
                "description": "Lead development of web applications, collaborated with cross-functional teams, and mentored junior developers."
            }
        ],
        "education": [
            {
                "degree": "Bachelor of Science in Computer Science",
                "school": "University of Engineering",
                "location": "Los Angeles, CA",
                "graduationDate": "May 2015"
            }
        ]
    }
    auditInformation = {
        "employer_username": "exampleUsername",
        "candidate": candidate_json.get("name"),
        "data_extraction_date": datetime.datetime.now()
    }
    celery_app.send_task(
        "app.auditEvent", args=[auditInformation], queue="audit_queue"
    )

    return candidate_json, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from linkedin_api import Linkedin
import re
import os
from dotenv import load_dotenv, dotenv_values 
load_dotenv() 

api = Linkedin(os.getenv("LINKEDIN_EMAIL"), os.getenv("LINKEDIN_PASSWORD"))
print(api)
print("getting profile")
profile = api.get_profile("jerry-waxman-591ab04")
print(profile["firstName"] + " " + profile["lastName"])


joblist = api.search_jobs(
    keywords="Software Engineer",  
    job_type=["I"],  
    experience=["1"],  
    limit=3,  
)

open("job_list.txt", "w").close()
for job in joblist:
    job_id_regex = re.findall(r"jobPosting:(\d+)", job["trackingUrn"])
    job_id = job_id_regex[0]
    print(job_id)
    print("Current Job: " + job["title"])
    job_data = api.get_job(job_id)
    job_description = job_data["description"]["text"]
    description = job_description.replace("\n", "")
    print(description)
    with open("job_list.txt", "a") as file:
        file.write(
            "{\n" + f"\tJob Name: \"{job['title']}\"\n"
            f'\tJob Description: "{description}"\n'
            f"\tJob Link: \"{'https://www.linkedin.com/jobs/view/' + job_id}\"\n"
            + "\n}\n"
        )

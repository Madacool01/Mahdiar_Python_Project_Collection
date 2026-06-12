import requests
import json
import time

APP_ID = "YOUR_ADZUNA_ID_HERE"
APP_KEY = "YOUR_APP_KEY_HERE"
COUNTRY = "at"

def scrape_jobs_for_all_keywords(keywords, location, radius_km = 15):
    unique_jobs = {}
    results_per_page = 50 #Maximum number of jobs per request

    for keyword in keywords:

        current_page = 1
        print(f"Searching for: {keyword}")

        while True:
            print(f"Fetching page {current_page}")


            url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{current_page}"

            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page" : results_per_page,
                "what": keyword, #Make a keywords list and scrape_jobs for each keyword in keywords.
                "content-type": "applications/json",
            }

            if location:
                params["where"] = location
                params["distance"] = radius_km
 
            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                results = data.get("results", [])

                if not results: #We have hit the final page of results --> we get an empty list []
                    print(f"No more jobs found for '{keyword}'. Next keyword")
                    break

                for job in results:
                    job_id = str(job.get("id")) #the adzuna id

                    if job_id not in unique_jobs:
                        unique_jobs[job_id] = {
                            "Title": job.get("title"),
                            "Company": job.get("company", {}).get("display_name"),
                            "Description": job.get("description"),
                            "URL": job.get("redirect_url"),
                            "Keyword Matched": keyword
                        }

                current_page+=1
                
                time.sleep(3) #Pause for 0.5 sec to avoid getting rate-limited (banned) by Adzuna.

            elif response.status_code == 429:
                print("Rate Limit reached. Waiting before trying again.")
                break
            else:
                print(f"Error: {response.status_code}")
                break
    return unique_jobs


if __name__ == "__main__": #We might import this later on.
    target_keywords = ["machienenbau", "projectleiter", "projectengineur", "project manager", "project engineer",
            "produktmanager", "mechanischer berechner", "konstrukteur", "design engineer", "mechanical design engineer"]

    jobs_dict = scrape_jobs_for_all_keywords(target_keywords, "Linz")

    print(f"Total unique jobs found: {len(jobs_dict)}")

    if len(jobs_dict) > 0:
        first_job = list(jobs_dict.values())[0]
        print(json.dumps(first_job, indent=4))

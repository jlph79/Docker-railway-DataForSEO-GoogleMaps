import json
from http.client import HTTPSConnection
from base64 import b64encode
from json import loads, dumps
import time
import os

DATAFORSEO_USERNAME=${DATAFORSEO_USERNAME}
DATAFORSEO_PASSWORD=${DATAFORSEO_PASSWORD}

# Define your task
keyword = "Computers Shops Accra"   

## Api Rest Connector for DataForSEO 
class RestClient:
    domain = "api.dataforseo.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password

    def request(self, path, method, data=None):
        connection = HTTPSConnection(self.domain)
        try:
            base64_bytes = b64encode(
                f"{self.username}:{self.password}".encode("ascii")
            ).decode("ascii")
            headers = {
                'Authorization': 'Basic %s' % base64_bytes,
                'Content-Encoding': 'gzip'
            }
            connection.request(method, path, headers=headers, body=data)
            response = connection.getresponse()
            return loads(response.read().decode())
        finally:
            connection.close()

    def get(self, path):
        return self.request(path, 'GET')

    def post(self, path, data):
        data_str = dumps(data) if not isinstance(data, str) else data
        return self.request(path, 'POST', data_str)
        
# Initialize RestClient with your credentials
RestClient = RestClient(DATAFORSEO_USERNAME, DATAFORSEO_PASSWORD)
 
# Function for to submit task to DataForSEO Servers
def submit_GoogleMaps_post_task(client,keyword):
    post_data = [{
        "location_name": "Ghana",
        "language_name": "English (United States)",
        "search_places": True,
        "max_crawl_pages": 100,
        "keyword": keyword
 
    }]
    response = client.post("/v3/serp/google/maps/task_post", post_data)
    print("Task submission response:", json.dumps(response, indent=2))  # Log the full response for debugging
    if response["status_code"] == 20000:
        task_ids = [task['id'] for task in response['tasks']]
        print("Task IDs created:", task_ids)
        return task_ids
    else:
        print(f"Error submitting tasks. Code: {response['status_code']} Message: {response['status_message']}")
        return None

def wait_for_task_completion(client, task_id):
    max_retries = 10  # Increase the number of retries
    wait_time = 30  # Increase the wait time to 30 seconds
    for attempt in range(max_retries):
        response = client.get(f"/v3/serp/google/maps/task_get/advanced/{task_id}")
        print(f"Checking task status for {task_id}: Attempt {attempt + 1}")
        if response["status_code"] == 20000:
            task_status = response['tasks'][0]['status_code']
            status_message = response['tasks'][0].get('status_message', 'No additional information')
            print(f"Task status: {task_status}, Message: {status_message}")
            if task_status == 20000:
                print("Task completed successfully.")
                return response  # Task completed successfully
            elif task_status == 40602 or task_status == 40601:
                print(f"Task {task_id} is still in queue or processing, status: {task_status}, waiting {wait_time} seconds to retry...")
                time.sleep(wait_time)
            else:
                print(f"Error with task. Task status code: {task_status}, message: {status_message}")
                return None  # An error occurred, no need to retry
        else:
            print(f"API error. Status code: {response['status_code']}, message: {response.get('status_message', 'No message available')}")
            return None  # API call failed, no need to retry
    print(f"Maximum retries reached for task ID {task_id}. Last checked status: {task_status}, message: {status_message}")
    return None  # Task did not complete within the retries


# Define the absolute path where you want to save the file
save_directory = os.path.abspath(os.path.join('..', 'Ghana - CTRT\DataForSEO'))
os.makedirs(save_directory, exist_ok=True)
file_path = os.path.join(save_directory, 'extracted_GoogleMapsDataset_raw.json')

# Submit review task and process results
task_ids = submit_GoogleMaps_post_task(RestClient, keyword)
if task_ids:
    for task_id in task_ids:
        response_GoogleMaps = wait_for_task_completion(RestClient, task_id)
        if response_GoogleMaps:
            print(json.dumps(response_GoogleMaps, indent=2))  # Convert the extracted data to JSON format and print
            # Save the extracted data to a JSON file
            with open(file_path, 'w') as json_file:  # Using absolute path for the file
                json.dump(response_GoogleMaps, json_file, indent=2)
            print(f"Data saved to {file_path}")
        else:
            print(f"Failed to retrieve or process reviews for task ID {task_id}.")
else:
    print("Failed to submit task.")
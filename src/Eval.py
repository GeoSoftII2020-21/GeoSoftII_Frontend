import datetime
import uuid
supportedJobs = ["ndvi", "sst","load_collection"]
jobDict = {
    "ndvi" : 443,
    "sst" : 444
}


def evalTaskAndQueue(task, datastore):
    for i in task["process"]["process_graph"]:
        if supportedJobs.__contains__(task["process"]["process_graph"][i]["process_id"]):
            task["id"] = uuid.uuid1()
            task["status"] = "created"
            task["created"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z" #Formatiert zeit zu RFC339
            datastore[task["id"]] = task
            return [True, task["id"]]
    return False

def evalTask(task):
    for i in task["process"]["process_graph"]:
        if supportedJobs.__contains__(task["process"]["process_graph"][i]["process_id"]):
            return True
    return False



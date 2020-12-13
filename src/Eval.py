from datetime import datetime
import uuid
supportedJobs = ["ndvi", "sst"]
jobDict = {
    "ndvi" : 443,
    "sst" : 444
}


def evalTask(task, datastore):
    if supportedJobs.__contains__(task["process"]["id"]):
        task["id"] = uuid.uuid1().int
        task["status"] = "created"
        task["created"] = datetime.now()
        datastore.append(task)
        return True
    return False

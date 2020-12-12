from datetime import datetime
supportedJobs = ["ndvi", "sst"]


def evalTask(task, datastore):
    if supportedJobs.__contains__(task["process"]["id"]):
        task["id"] = "Test"
        task["status"] = "queued"
        task["created"] = datetime.now()
        datastore.append(task)
        return True
    return False

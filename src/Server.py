import os
import uuid
import datetime
import requests
from flask import Flask, request, jsonify, Response, send_from_directory, make_response
from flask_cors import CORS
import json
import xarray
import time

app = Flask(__name__)
CORS(app)

docker = False


Datastore = {}
exc = {}




@app.route("/api/v1/", methods=['GET'])
def default():
    """
    Default Endpoint. Returns a json which contains the description
    :return: JSON
    """
    data = {"api_version": "1.0.0", "backend_version": "1.1.2", "stac_version": "string", "id": "cool-eo-cloud",
            "title": "WWU Geosoft2 Projekt", "description": "WWU Projekt", "production": False,
            "endpoints": [{"path": "/collections", "methods": ["GET"]},
                          {"path": "/processes", "methods": ["GET"]},
                          {"path": "/jobs", "methods": ["GET", "POST"]},
                          {"path": "/jobs/{job_id}", "methods": ["DELETE", "PATCH"]},
                          {"path": "/jobs/{job_id}/results", "methods": ["GET", "POST"]},
                          {"path": "/jobs/{job_id}", "methods": ["GET"]},
                          ], "links": [
            {"href": "https://www.uni-muenster.de/de/", "rel": "about", "type": "text/html",
             "title": "Homepage of the service provider"}]}
    return jsonify(data)


@app.route("/.well-known/openeo", methods=["GET"])
@app.route("/api/v1/.well-known/openeo", methods=["GET"])
def wellKnownEO():
    """
    Implements the well known openeo endpoint

    :returns:
        jsonify(data): JSON
    """
    data = {
        "versions": [
            {
                "url": "http://localhost/api/v1",
                "api_version": "1.0.0",
                "production": False
            },
        ]
    }
    return jsonify(data)


@app.route("/api/<string:version>/collections", methods=['GET'])
def collections(version):
    """
    Returns the collections description

    :returns:
        jsonify(data): Collections description in a json
    """
    if (version == "v1"):
        with open("json/collection_description.json") as json_file:
            data = json.load(json_file)
        return jsonify(data)
    else:
        data = {
            "message": "Invalid API Version.",
            "level" : "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/processes", methods=['GET'])
def processes(version):
    """
    Returns the process description

    :returns:
        jsonify(data): Process Description
    """
    if (version == "v1"):
        with open("json/process_description.json") as json_file:
            data = json.load(json_file)
        return jsonify(data)
    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs", methods=['GET'])
def jobsGET(version):
    """
    Returns all saved Jobs
    :returns:
        jsonify(data): All jobs which are sent to the server in a JSON
    """
    if (version == "v1"):
        data = {
            "jobs": [
            ],
            "links": [
                {
                    "rel": "related",
                    "href": "https://example.openeo.org",
                    "type": "text/html",
                    "title": "openEO"
                }
            ]
        }
        for i in Datastore:
            data["jobs"].append(Datastore[i])
        return jsonify(data)
    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs", methods=['POST'])
def jobsPOST(version):
    """
    Takes a given job an puts it in the Datastore
    :param version:
    :return: returns a header which shows the lcoation and id
    """
    if (version == "v1"):
        dataFromPost = request.get_json()  # Todo: JSON Evaluieren
        id = uuid.uuid1()
        Datastore[id] = dataFromPost
        Datastore[id]["id"] = id
        Datastore[id]["status"] = "created"
        Datastore[id]["created"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[
                          :-4] + "Z"  # Formatiert zeit zu RFC339
        resp = Response(status=201)
        resp.headers["Location"] = "localhost/api/v1/jobs/" + str(id)
        resp.headers["OpenEO-Identifier"] = str(id)
        return resp


    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs/<uuid:id>", methods=['PATCH'])
def patchFromID(version, id):
    """
    Takes the body of a patch request and replaces the body with the specified id
    :parameter:
        id (UUID): id
        version (string): API Version
    :returns:
        jsonify(data): status code
    """
    dataFromPatch = request.get_json()
    if version == "v1":
        if Datastore[id]["status"] != "running":
            dataFromPatch["created"] = Datastore[id]["created"]
            dataFromPatch["updated"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z"
            Datastore[id] = dataFromPatch
            return Response(status=204)
    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs/<uuid:id>", methods=["DELETE"])
def deleteFromID(version, id):
    """
    Takes a delete request and deletes the job
    :parameter:
        id (UUID): Job id
        version (string): API Version
    :returns:
        jsonify(data): http statuscode
    """
    if (version == "v1"):
        Datastore[uuid.UUID(str(id))]["status"] = "canceled"
        return Response(status=204)
    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=['POST'])
def startFromID(version, id):
    """
    Starts a job which is already saved in the datastore
    :parameter:
        id (UUID): Job ID
        version (string): API Version
    :returns:
        jsonify(data): HTTP Statuscode
    """
    if (version == "v1"):
        try:
            Datastore[id]["start_datetime"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[
                              :-4] + "Z"
            Datastore[id]["status"] = "queued"
            job = Datastore[id]
            temp = dict(job)
            temp["id"] = str(job["id"])
            if docker:
                requests.post("http://processManager:80/takeJob", json=temp)
            else:
                requests.post("http://localhost:440/takeJob", json=temp)
            return Response(status=202)
        except KeyError:
            data = {
                "message": "Invalid Job ID Call.",
                "level": "error",
                "code": "KeyError"
            }
            resp = make_response(jsonify(data), 404)
            return resp
        except:
            data = {
                "message": "Invalid API Call.",
                "level": "error",
                "links": [
                    {
                        "href": "http://localhost/api/v1/.well-known/openeo",
                        "rel": "about"
                    }
                ]
            }
            resp = make_response(jsonify(data), 404)
            return resp
    else:
        data = {
            "message": "Invalid API Call.",
            "level": "error",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=["GET"])
def getJobFromID(version, id):
    """
    Takes the bod yfrom aget request and returns the result
    :parameter:
        id (UUID): Job ID
        version (string): API Version
    :returns:
        jsonify(data): Job Result.
    """
    if (version == "v1"):
        try:
            if Datastore[uuid.UUID(str(id))]["status"] == "error":
                data = {
                    "id": str(uuid.uuid1()),
                    "level": "error",
                    "message": "Forwarded Error" + str(exc[uuid.UUID(str(id))])
                }
                resp = make_response(jsonify(data), 424)
                return resp
            if Datastore[uuid.UUID(str(id))]["status"] == "finished":
                returnVal = {
                    "stac_version":  "1.0.0",
                    "id": id,
                    "type": "Feature",
                    "geometry": None, #Rücksprache was das ist?
                    "properties": {
                        "datetime": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z",
                        "start_datetime": Datastore[uuid.UUID(str(id))]["start_datetime"],
                        "end_datetime": Datastore[uuid.UUID(str(id))]["end_datetime"],
                        "title": Datastore[uuid.UUID(str(id))]["title"],
                        "description": Datastore[uuid.UUID(str(id))]["description"],
                        "created": Datastore[uuid.UUID(str(id))]["created"],
                    },
                    "assets":  {
                    },
                    "links": []
                }
                if "updated" in Datastore[uuid.UUID(str(id))]:
                    returnVal["properties"]["updated"] = Datastore[uuid.UUID(str(id))]["updated"],
                for filename in os.listdir("data/"+ str(id)+"/saves/"):
                    returnVal["assets"][filename] = {"href": "http://localhost:80/download/"+str(id)+"/"+str(filename)[:-3]}
                return jsonify(returnVal)
            if Datastore[uuid.UUID(str(id))]["status"] == "running":
                data = {
                    "id": str(uuid.uuid1()),
                    "level": "error",
                    "message": "Data is Processing"
                }
                resp = make_response(jsonify(data), 404)
                return resp
        except KeyError:
            data = {
                "message": "Invalid Job ID Call.",
                "level": "error",
                "code": "KeyError"
            }
            resp = make_response(jsonify(data), 404)
            return resp
        except:
            data = {
                "message": "Invalid API Call.",
                "id": str(uuid.uuid1()),
                "links": [
                    {
                        "href": "http://localhost/api/v1/.well-known/openeo",
                        "rel": "about"
                    }
                ]
            }
            resp = make_response(jsonify(data), 404)
            return resp
        data = {
            "id": str(uuid.uuid1()),
            "level": "error",
            "message": "A unkown error Occured."
        }
        resp = make_response(jsonify(data), 404)
        return resp
    else:
        data = {
            "code": str(uuid.uuid1()),
            "message": "Invalid API Call."
        }
        resp = make_response(jsonify(data), 404)
        return resp

@app.route("/api/<string:version>/jobs/<uuid:id>",methods=["GET"])
def getjob(version, id):
    """
    Returns the job
    :param version: API Version
    :param id: ID
    :return:
    """
    if version=="v1":
        return jsonify(Datastore[uuid.UUID(str(id))])
    else:
        data = {
            "level" : "error" ,
            "message": "Invalid API Call.",
            "links": [
                {
                    "href": "http://localhost/api/v1/.well-known/openeo",
                    "rel": "about"
                }
            ]
        }
        resp = make_response(jsonify(data), 404)
        return resp

@app.route("/download/<uuid:id>/<uuid:subid>")
def download(id, subid):
    """
    Download method for the netcdf
    :param version: API Version
    :param id: ID
    :return: Netcdf file
    """
    name = str(subid)+".nc"
    return send_from_directory("data/"+str(id)+"/saves",filename=name, as_attachment=True,attachment_filename=name, mimetype="application/x-netcdf")



@app.route("/data", methods=["POST"])
def postData():
    """
    Custom Route, Should enable a collection post. Not Yet Implemented
    :returns:
        jsonify(data): HTTP Statuscode  (?)
    """
    return Response(status=500)


@app.route("/jobRunning/<uuid:id>", methods=["GET"])
def jobUpdate(id):
    """
    Set the Job status if not canceled
    :param id: ID
    :return: Job JSON
    """
    if Datastore[id]["status"] == "queued":
        Datastore[id]["status"] = "running"
        Datastore[id]["start_datetime"]=datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z"
        return jsonify(Datastore[id])
    elif Datastore[id]["status"] != "queued":
        return Datastore[id]


@app.route("/takeData/<uuid:id>", methods=["POST"])
def takeData(id):
    """
    Takes the job result and puts it in the datastore
    :rtype: Response Object
    """
    Datastore[id]["end_datetime"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z" #Formatiert zeit zu RFC339
    Datastore[id]["status"] = request.args["status"]
    if Datastore[id]["status"] == "error":
        exc[uuid.UUID(str(id))] = request.args["errorType"]
    return Response(status=200)


def serverBoot():
    """
    Starts the application
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    app.run(debug=True, host="0.0.0.0", port=80)


if __name__ == "__main__":
    serverBoot()

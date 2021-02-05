import os
import uuid
import datetime
import requests
from flask import Flask, request, jsonify, Response, send_from_directory, make_response
from flask_cors import CORS
import json
import xarray


app = Flask(__name__)
CORS(app)

docker = False


Datastore = {}
exc = {}




@app.route("/api/v1/", methods=['GET'])
def default():
    """
    Soll ein JSON mit der Kurzübersicht unserer API Returnen
    :return: JSON
    """
    # Todo: Anpassen
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
    Implementiert abfrage für Supported openEO Versions auf wunsch von Judith.
    Evtl. Antwort noch anpassen. Ich bin mir noch nicht ganz sicher ob das so richtig ist. Insbesondere weiß ich nicht welche version wir implementieren.

    :returns:
        jsonify(data): JSON mit der Unterstützen API Version und ein verweis auf diese.
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
    Returnt alle vorhandenen Collections bei einer GET Request
    Collections sollten evtl im dezidierten server gelistet sein, entsprechend sollte dort die Antwort generiert werden

    :returns:
        jsonify(data): Alle Collections in einer JSON
    """
    # Todo: Abfrage an Daten Managment System über welche Collections wir überhaupt verfügen
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
    Returnt alle vorhandenen processes bei einer GET Request
    Quelle für NDVI: https://github.com/Open-EO/openeo-processes/blob/master/ndvi.json

    :returns:
        jsonify(data): Alle processes in einer JSON
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
    Returnt alle vorhandenen jobs bei einer GET Request
    :returns:
        jsonify(data): Alle jobs in einer JSON
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
    Nimmt den Body eines /jobs post request entgegen. Wichtig: Startet ihn NICHT!
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    if (version == "v1"):
        dataFromPost = request.get_json()  # Todo: JSON Evaluieren
        id = uuid.uuid1()
        Datastore[id] = dataFromPost
        Datastore[id]["id"] = id
        Datastore[id]["status"] = "created"
        Datastore[id]["created"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[
                          :-4] + "Z"  # Formatiert zeit zu RFC339
        resp = Response(status=200)
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
    Nimmt den Body einer Patch request mit einer ID entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
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
    Nimmt eine Delete request für eine ID Entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
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
    Startet einen Job aufgrundlage einer ID aus der URL. Nimmt ebenso den Body der Post request entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    if (version == "v1"):
        Datastore[id]["start_datetime"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[
                          :-4] + "Z"
        Datastore[uuid.UUID(str(id))]["status"] = "queued"
        job = Datastore[uuid.UUID(str(id))]
        temp = dict(job)
        temp["id"] = str(job["id"])
        if docker:
            requests.post("http://processManager:80/takeJob", json=temp)
        else:
            requests.post("http://localhost:440/takeJob", json=temp)
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


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=["GET"])
def getJobFromID(version, id):
    """
    Nimmt den Body einer GET request mit einer ID entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): Ergebnis des Jobs welcher mit der ID assoziiert ist.
    """
    if (version == "v1"):
        if Datastore[uuid.UUID(str(id))]["status"] == "error":
            data = {
                "id": str(uuid.uuid1()),
                "level": "error",
                "message": exc[uuid.UUID(str(id))]
            }
            resp = make_response(jsonify(data), 424)
            return resp
        if Datastore[uuid.UUID(str(id))]["status"] == "done":
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
                returnVal["assets"][filename] = {"href": "http://localhost:8080/download/"+str(id)+"/"+str(filename)[:-3]}
            return jsonify(returnVal)
        if Datastore[uuid.UUID(str(id))]["status"] == "running":
            data = {
                "id": str(uuid.uuid1()),
                "level": "error",
                "message": "Date is Processing"
            }
            resp = make_response(jsonify(data), 404)
            return resp
        data = {
            "id": str(uuid.uuid1()),
            "level": "error",
            "message": "A unkown error Occured"
        }
        resp = make_response(jsonify(data), 404)
        return resp
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

@app.route("/api/<string:version>/jobs/<uuid:id>",methods=["GET"])
def getjob(version, id):
    if version=="v1":
        return jsonify([uuid.UUID(str(id))])
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
    name = str(subid)+".nc"
    return send_from_directory("data/"+str(id)+"/saves",filename=name, as_attachment=True,attachment_filename=name, mimetype="application/x-netcdf")



@app.route("/data", methods=["POST"])
def postData():
    """
    Custom Route, welche nicht in der OpenEO API Vorgesehen ist. Nimmt die daten der Post request entgegen.
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPost = request.get_data()
    f = open('data/sst.day.mean.1984.v2.nc', 'w+b')
    binary_format = bytearray(dataFromPost)
    f.write(binary_format)
    f.close()
    return Response(status=200)


@app.route("/jobRunning/<uuid:id>", methods=["GET"])
def jobUpdate(id):
    """
    Aktualisiert den Job status sofern er nicht abgebrochen wurde
    :param id: ID
    :return: Json mit Job
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
    Nimmt das ergebnis eines jobs entgegen und fügt ihm den Datastore hinzu
    :rtype: Response Object
    """
    Datastore[id]["end_datetime"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-4]+"Z" #Formatiert zeit zu RFC339
    Datastore[id]["status"] = request.args["status"]
    if Datastore[id]["status"] == "error":
        exc[uuid.UUID(str(id))] = request.args["errorType"]
    return Response(status=200)


def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    app.run(debug=True, host="0.0.0.0", port=8080)  # Todo: Debug  Ausschalten, Beißt sich  mit Threading


if __name__ == "__main__":
    serverBoot()

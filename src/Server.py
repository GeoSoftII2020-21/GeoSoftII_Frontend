import os
import uuid

import requests
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import Eval

app = Flask(__name__)
CORS(app)

docker = False


Datastore = {}




@app.route("/api/v1/", methods=['GET'])
def default():
    """
    Soll ein JSON mit der Kurzübersicht unserer API Returnen
    :return: JSON
    """
    # Todo: Anpassen
    data = {"api_version": "1.0.0", "backend_version": "1.1.2", "stac_version": "string", "id": "cool-eo-cloud",
            "title": "WWU Geosoft2 Projekt", "description": "WWU Projekt", "production": False,
            "endpoints": [{"path": "/collections", "methods": ["GET"]}, {"path": "/processes", "methods": ["GET"]},
                          {"path": "/jobs", "methods": ["GET", "POST"]},
                          {"path": "/jobs/{job_id}", "methods": ["DELETE", "PATCH"]},
                          {"path": "/jobs/{job_id}/result", "methods": ["GET", "POST"]}], "links": [
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
        data = {
            "collections": [
                {
                    "stac_version": "",
                    "id": "SST-Geosoft2",
                    "title": "global SST data based on the NOAA OI SST V2 High Resolution Dataset",
                    "description": "SST data based on the NOAA OI SST V2 High Resolution Dataset Data from 1981 up to today on a 1/4 deg global grid Saved as NetCDF file and provided as xArray See more details: https://psl.noaa.gov/data/gridded/data.noaa.oisst.v2.highres.html#detail",
                    "keywords": ["SST", "Geosoft", "NOAA", "global"],
                    "version": "1.0",
                    "license": "",
                    "providers": "NOAA",
                    "spatial_extent": {
                        "west": "0.125E",
                        "south": "89.875S",
                        "east": "359.875E",
                        "north": "89.875N",
                        "crs": ""
                    },
                    "temporal_extent": [
                        "1981-09-01T00:00:00Z",
                        "2020-12-31T23:59:59Z"
                    ],
                    "bands": ["SST"],
                    "links": "https://psl.noaa.gov/data/gridded/data.noaa.oisst.v2.highres.html#detail",
                    "cube": "dimensions:{x:1424,y:720,z:1,t:'40years',bands:1}"
                },
                {
                    "stac_version": "",
                    "id": "Sentinel2-Geosoft2",
                    "title": "Sentinel 2 based NDVI-bands",
                    "description": "Sentinel 2 based NDVI-bands Bands needed for the NDVI based on Sentinel 2 data With a 100x100m grid for the area of Münster for 2017-2020",
                    "keywords": ["S2", "Geosoft", "Sentinel2", "Sentinel", "NDVI"],
                    "version": "1.0",
                    "license": "",
                    "providers": "Copernicus",
                    "spatial_extent": {
                        "west": 7.5315289026,
                        "south": 51.3631578425,
                        "east": 9.1432907668,
                        "north": 52.35038628320001,
                        "crs": ["EPSG:32631", "EPSG:32632"]
                    },
                    "temporal_extent": [
                        "2017-01-01T00:00:00Z",
                        "2020-12-31T23:59:59Z"
                    ],
                    "bands": [
                        "B4",
                        "B8"
                    ]
                    ,
                    "links": "https://scihub.copernicus.eu/",
                    "cube": "dimensions:{x:1830,y:1830,z:1,t:'3years',bands:2}"
                }

            ],
            "links": [
                {
                    "rel": "alternate",
                    "href": "https://example.openeo.org/csw",
                    "title": "openEO catalog (OGC Catalogue Services 3.0)"
                }
            ]
        }  # Todo: Anpassen
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/processes", methods=['GET'])
def processes(version):
    """
    Returnt alle vorhandenen processes bei einer GET Request
    Quelle für NDVI: https://github.com/Open-EO/openeo-processes/blob/master/ndvi.json

    :returns:
        jsonify(data): Alle processes in einer JSON
    """
    if (version == "v1"):
        data = {
            "processes": [
                {
                    "processes": [
                        {
                            "id": "ndvi",
                            "summary": "Normalized Difference Vegetation Index",
                            "description": "Computes the Normalized Difference Vegetation Index (NDVI). The NDVI is computed as *(nir - red) / (nir + red)*.\n\nThe `data` parameter expects a raster data cube as NetCDF including Sentinel2-Data. This cube has three dimensions and two data variables. Dimension are time, lon and lat while data variables are red and nir.\n\n. As a result of the computation, a NetCDF-File including the NDVI-values is created in the given path.",
                            "categories": [
                                "math > indices",
                                "vegetation indices"
                            ],
                            "parameters": [
                                {
                                    "name": "data",
                                    "description": "Name of data input / data cube.",
                                    "schema": {
                                        "type": "object",
                                        "subtype": "raster-cube"
                                    }
                                },
                                {
                                    "name": "nir",
                                    "description": "Represents all nir-bands that are relevant for NDVI calculation within a given time horizon.",
                                    "schema": {
                                        "type": "xarray",
                                        "subtype": "xarray.core.dataarray.DataArray"
                                    },
                                },
                                {
                                    "name": "red",
                                    "description": "Represents all red-bands that are relevant for NDVI calculation within a given time horizon.",
                                    "schema": {
                                        "type": "xarray",
                                        "subtype": "xarray.core.dataarray.DataArray"
                                    },
                                }
                            ],
                            "returns": {
                                "description": "A dask.delayed.Delayed object containing the computed NDVI values. Additionally, this is saved as NetCDF under the given path.",
                                "schema": {
                                    "type": "object",
                                    "subtype": "raster-cube"
                                }
                            },
                            "exceptions": {
                                "ValueError": {
                                    "message": "Red or Nir is empty."
                                }
                            },
                            "links": [
                                {
                                    "rel": "about",
                                    "href": "https://en.wikipedia.org/wiki/Normalized_difference_vegetation_index",
                                    "title": "NDVI explained by Wikipedia"
                                },
                                {
                                    "rel": "about",
                                    "href": "https://earthobservatory.nasa.gov/features/MeasuringVegetation/measuring_vegetation_2.php",
                                    "title": "NDVI explained by NASA"
                                }
                            ]
                        }
                    ]
                },
                {
                    "id": "mean_sst",
                    "summary": "Mean Sea Surface Temperature",
                    "description": "Computes the arithmatic mean of sst data. The arithmetic mean is defined as the sum of all elements divided by the number of elements. The user defines a timeframe and optionally also a spatial subset, for which the mean is to be computed. For each day in the given timeframe the sea surface temperature values for a cell are summed up and divided by the number of days in the timeframe. This is done for all cells within the spatial subset or, if no bounding box was defined, for all cells in the dataset.",
                    "categories": [
                        "math",
                        "reducer"
                    ],
                    "parameters": [
                        {
                            "name": "data",
                            "description": "A raster data cube containing sst data.",
                            "schema": {
                                "type": "object",
                                "subtype": "raster-cube"
                            }
                        },
                        {
                            "name": "timeframe",
                            "description": "An array with two values: [start date, end date]. Timeframe values are strings of the format 'year-month-day'. For example: '1981-01-01'.",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "subtype": "date"
                                }
                            }
                        },
                        {
                            "name": "bbox",
                            "description": "An array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. For example: [0,-90,360,90]",
                            "schema": {
                                "type": "array",
                                "items": {
                                    "type": "number"
                                }
                            },
                            "optional": True
                        }
                    ],
                    "returns": {
                        "description": "A raster data cube containing the computed mean sea surface temperature.",
                        "schema": {
                            "type": "object",
                            "subtype": "raster-cube"
                        }
                    },
                    "exceptions": {
                        "InvalidBboxLengthError": {
                            "message": "Parameter bbox is an array with four values: [min Longitude, min Latitude, max Longitude, max Latitude]. Please specify an array with exactly four values."
                        },
                        "InvalidLongitudeValueError": {
                            "message": "Longitude is out of bounds."
                        },
                        "InvalidLatitudeValueError": {
                            "message": "Latitude is out of bounds."
                        },
                        "InvalidTimeframeLengthError": {
                            "message": "Parameter timeframe is an array with two values: [start date, end date]. Please specify an array with exactly two values."
                        },
                        "InvalidTimeframeValueError": {
                            "message": "Timeframe values are strings of the format 'year-month-day'. For example '1981-01-01'. Please specify timeframe values that follow this format."
                        },
                        "ValueError": {
                            "message": "The timeframe values are invalid. Please specify actual dates as start and end date. "
                        }
                    },
                    "links": [
                        {
                            "rel": "about",
                            "href": "https://en.wikipedia.org/wiki/Arithmetic_mean",
                            "title": "Arithmetic mean explained by Wikipedia"
                        },
                        {
                            "rel": "about",
                            "href": "https://en.wikipedia.org/wiki/Sea_surface_temperature",
                            "title": "Sea surface temperature explained by Wikipedia"
                        }
                    ]
                }

            ],

            "links": [
                {
                    "rel": "alternate",
                    "href": "https://provider.com/processes",
                    "type": "text/html",
                    "title": "HTML version of the processes"
                }
            ]
        }  # Todo: Anpassen, Dev Team beauftragen das gleiche für SST zu schreiben, von Dev Team Verifizieren Lassen
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


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
        }  # Todo: Anpassen
        for i in Datastore:
            data["jobs"].append(Datastore[i])
        return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs", methods=['POST'])
def jobsPOST(version):
    """
    Nimmt den Body eines /jobs post request entgegen. Wichtig: Startet ihn NICHT!
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """

    # Todo: Funktion schreiben die auswertet was im JSON steht...
    if (version == "v1"):
        dataFromPost = request.get_json()  # Todo: JSON Evaluieren
        ev = Eval.evalTaskAndQueue(dataFromPost, Datastore)
        if (ev[0]):
            resp = Response()
            resp.headers["Location"] = "localhost/api/v1/jobs/" + str(ev[1])
            resp.headers["OpenEO-Identifier"] = str(ev[1])
            return resp
        else:
            data = {
                "id": "",  # Todo: ID Generieren bzw. Recherchieren
                "code": "400",
                "message": "Unbekannter Job Typ.",
                "links": [
                    {
                        "href": "https://example.openeo.org/docs/errors/SampleError",
                        # Todo: Passenden Link Recherchieren & Einfügen
                        "rel": "about"
                    }
                ]
            }
            return jsonify(data)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


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
    if (version == "v1"):
        if Eval.evalTask(dataFromPatch):
            Datastore[uuid.UUID(id)] = dataFromPatch
        else:
            data = {
                "id": "",  # Todo: ID Generieren bzw. Recherchieren
                "code": "404",
                "message": "Ungültiger API Aufruf.",
                "links": [
                    {
                        "href": "https://example.openeo.org/docs/errors/SampleError",
                        # Todo: Passenden Link Recherchieren & Einfügen
                        "rel": "about"
                    }
                ]
            }
            return jsonify(data)


    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>", methods=["DELETE"])
def deleteFromID(version, id):
    """
    Nimmt eine Delete request für eine ID Entgegen
    Todo: Herausfinden wie man das Umsetzt. Irgendwie müssen wir laufende Dask Prozesse Terminieren.
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    if (version == "v1"):
        Datastore[uuid.UUID(id)]["status"] = "created"
        return Response(status=204)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=['POST'])
def startFromID(version, id):
    """
    Startet einen Job aufgrundlage einer ID aus der URL. Nimmt ebenso den Body der Post request entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    #Todo: Datastore sollte immer alle elemente beinhalten
    if (version == "v1"):
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
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/api/<string:version>/jobs/<uuid:id>/results", methods=["GET"])
def getJobFromID(version, id):
    """
    Nimmt den Body einer GET request mit einer ID entgegen
    :parameter:
        id (int): Nimmt die ID aus der URL entgegen
    :returns:
        jsonify(data): Ergebnis des Jobs welcher mit der ID assoziiert ist.
    """
    bbox = []
    for i in Datastore[uuid.UUID(id)]:
        for j in Datastore[uuid.UUID(id)]["process"]["process_graph"]:
            if Datastore[uuid.UUID(id)]["process"]["process_graph"][j]["id"] == "load_collection":
                bbox.append(Datastore[uuid.UUID(id)]["process"]["process_graph"][j]["arguments"]["spatial_extent"])
    if (version == "v1"):
        returnVal = {
            "stac_version" :  "string",
            "stac_extensions" : [],
            "id" : id,
            "type" : "Feature",
            "bbox" : bbox,
            "geometry" : None, #Rücksprache was das ist?
            "assets" :  None, #Rücksprache was wir überhaupt für
            "links" : []
        }
        return jsonify(returnVal)
    else:
        data = {
            "id": "",  # Todo: ID Generieren bzw. Recherchieren
            "code": "404",
            "message": "Ungültiger API Aufruf.",
            "links": [
                {
                    "href": "https://example.openeo.org/docs/errors/SampleError",
                    # Todo: Passenden Link Recherchieren & Einfügen
                    "rel": "about"
                }
            ]
        }
        return jsonify(data)


@app.route("/data", methods=["POST"])
def postData():
    """
    Custom Route, welche nicht in der OpenEO API Vorgesehen ist. Nimmt die daten der Post request entgegen.
    Todo: Evtl. Verschieben das der Upload nur noch von der Lokalen Maschine aus möglich ist?
    :returns:
        jsonify(data): HTTP Statuscode für Erfolg (?)
    """
    dataFromPost = request.get_json()
    if docker:
        r = requests.post("http://database:80/data", json=dataFromPost)
    else:
        r = requests.post("http://localhost:443/data", json=dataFromPost)
    data = r.json()
    return data


@app.route("/jobRunning/<uuid:id>", methods=["GET"])
def jobUpdate(id):
    """
    Aktualisiert den Job status sofern er nicht abgebrochen wurde
    :param id: ID
    :return: Json mit Job
    """
    if Datastore[uuid.UUID(id)]["status"] == "queued":
        Datastore[uuid.UUID(id)]["status"] = "running"
        return Datastore[uuid.UUID(id)]
    elif Datastore[uuid.UUID(id)]["status"] == "created":
        return Datastore[uuid.UUID(id)]


@app.route("/takeData/<uuid:id>", methods=["POST"])
def takeData(id):
    """
    Nimmt das ergebnis eines jobs entgegen und fügt ihm den Datastore hinzu
    :rtype: Response Object
    """
    Datastore[uuid.UUID(id)]["result"] = request.get_json()
    return Response(status=200)


def serverBoot():
    """
    Startet den Server. Aktuell im Debug Modus und Reagiert auf alle eingehenden Anfragen auf Port 80.
    """
    global docker
    if os.environ.get("DOCKER") == "True":
        docker = True
    app.run(debug=True, host="0.0.0.0", port=80)  # Todo: Debug  Ausschalten, Beißt sich  mit Threading


if __name__ == "__main__":
    serverBoot()

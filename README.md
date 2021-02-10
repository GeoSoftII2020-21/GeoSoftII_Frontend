# GeoSoftII_Frontend
### Geosoftware II project WiSe 2020/21
---

## Table of contents
[1. Overview](#overview) \
[2. Installation](#install) \
[3. Scope of functionalities](#functionalities)  \
[4. Examples of use](#use) \
[5. Appendix](#annex) \
\
<a name="overview"><h3>Overview</h3></a>
This project is part of a new [openEO](https://openeo.org/) back-end driver which uses the [Pangeo Software Stack](https://pangeo.io/).

The goal is to provide a openEO compliant HTTP API which can communicate with other micorservices in the project. It can create and execute batch jobs. These jobs load data and execute two predefined processes. For more information on the other micorservices you can look at their repositories:
1. [Data storage](https://github.com/GeoSoftII2020-21/GeoSoftII_DataServer)
2. [NDVI calculation](https://github.com/GeoSoftII2020-21/GeoSoftII_NDVI_Process)
3. [SST calculation](https://github.com/GeoSoftII2020-21/GeoSoftII_SST_Process)

This subproject covers the points [/F0010/ to /F0060/](https://docs.google.com/document/d/1WoATTUVsINCdbQf7znDNLueZm17Sar1JBZDKQGBunbE/edit#heading=h.mrpj8lyegpld) of the requirements.

There also exists a [Docker Repository](https://hub.docker.com/r/felixgi1516/geosoft2_frontend), which is linked with this one and from which the service can be obtained as an image. And can then be used locally as a container.


\
<a name="install"><h3>Installation</h3></a>
The installation and execution is possible exclusively provided within the framework of the *[docker-compose.yml](https://github.com/GeoSoftII2020-21/GeoSoftII_Projekt/blob/Docker-compose/docker-compose.yml)*.
```docker
docker-compose up
```
You can now checkout every [endpoint](#endpoints) with the base url [localhost/api/v1/](http://localhost/api/v1/).


\
<a name="functionalities"><h3>Scope of functionalities</h3></a>

This HTTP API is structured after the [openEO API specification](https://open-eo.github.io/openeo-api/). At the moment only the most basic endpoints are implemented.

The first main function of this microservice is to provide basic information on the processes and collections offered by the whole project under the endpoints /processes and /collections.  The second one is to create, change and execute the batch jobs which can start the other microservices.  


#### API endpoints

- `GET /collections` List all available collections
- `GET /processes` Lists all available processes
- `GET /jobs` Lists all created batch jobs
- `POST /jobs` Creates a new batch job with the posted JSON
- `GET /jobs/{job_id}/` Returns information about the specified job
- `DELETE /jobs/{job_id}/` Deletes the specified job
- `PATCH /jobs/{job_id}/` Updates the specified job with posted JSON
- `GET /jobs/{job_id}/results` Get a download link for the specified job

\
<a name="annex"><h3>Appendix</h3></a>

#### Technologies
Software | Version
------ | ------
[flask](https://flask.palletsprojects.com/en/1.1.x/) | 1.1.2
[requests](https://requests.readthedocs.io/en/master/)   | 2.25.0 | 2.25.0
[flask_cors](https://flask-cors.readthedocs.io/en/latest/) | 3.0.9
[xarray](http://xarray.pydata.org/en/stable/) | 0.16.1
[dask](https://dask.org/) | 2.30.0
[numpy](https://numpy.org/) | 1.19.3
[scipy](https://www.scipy.org/) | 1.6.0
[netCDF4](https://unidata.github.io/netcdf4-python/netCDF4/index.html) | 1.19.3

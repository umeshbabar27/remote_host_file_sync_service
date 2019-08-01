#Remote Host File Sync Service
=================


This repository contains #Remote Host File Sync Service code for a RESTful API based on Flask and Flask-RESTPlus.


This service is responsible for deploying and configuration of Remote Host File Sync Service on to remote host.


Rest APIs
=================
/rhfsServices

The /rhfsServices rest API will be used to:

    Get the list of saved remote host file sync Services. (get /rhfsServices)
    Manage a new remote host file sync Service. (post /rhfsServices)
    Edit properties of an existing remote host file sync Service (put /rhfsServices/id)
    Unmanage an remote host file sync Service (delete /rhfsServices/id)

GET /rhfsServices

Use the GET /rhfsServices request to get the list of currently managed remote host file sync Service.
Response Body Example

[

    {

        “id”: 0,

        “address”: “10.243.23.55,

        “description”: “primary rhfsServices for example servers.”,

        “publicKey”: {

            “algorithm”: “ecdsa-sha2-nistp256”,

            “key”: “AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEHWZnXOySMOv8GAium4X3oBOLWHBQos0MAsEudLcz1DnHdFsJAOX1VqYcZot0NN3BO8xwoltqTK1ITMCps4c50=”

        },

        "diskUsage": {"total": 4096, "used": 1024, "free" 3072},

        "state": "online",

    },


GET /rhfsServices/id

Use the GET /rhfsServices/id request to get a currently-managed remote host file sync Services  by its automatically-generated id.
Response Body Example


{

    “id”: 0,

    “address”: “10.234.23.55”,

    “description”: “primary rhfsServices for example servers”,

    “publicKey”: {

        “algorithm”: “ecdsa-sha2-nistp256”,

        “key”: “AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEHWZnXOySMOv8GAium4X3oBOLWHBQos0MAsEudLcz1DnHdFsJAOX1VqYcZot0NN3BO8xwoltqTK1ITMCps4c50=”

    },


     "diskUsage": {"total": 4096, "used": 1024, "free" 3072},

     "state": "online",

}
POST /rhfsServices

Use the POST /rhfsServices request to manage (create) a new remote host file sync Services.
Request Body Example

{

    “address”: “10.243.23.55,

    “description”: “rhfsServices service for remote servers.”,

    “publicKey”: {

        “algorithm”: “ecdsa-sha2-nistp256”,

        “key”: “AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEHWZnXOySMOv8GAium4X3oBOLWHBQos0MAsEudLcz1DnHdFsJAOX1VqYcZot0NN3BO8xwoltqTK1ITMCps4c50=”

    },


    "diskUsage": {"total": 4096, "used": 1024, "free" 3072},

    "state": "online",

}
PUT /rhfsServices/id


Use the PUT /rhfsServices/id request to update the properties of an remote host file sync Services.
Request Body Example

{

    “id”: 0,

    “address”: “10.243.23.55”,

    “description”: “remote host file sync Service for remote servers.”,

    “publicKey”: {

        “algorithm”: “ecdsa-sha2-nistp256”,

        “key”: “AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBEHWZnXOySMOv8GAium4X3oBOLWHBQos0MAsEudLcz1DnHdFsJAOX1VqYcZot0NN3BO8xwoltqTK1ITMCps4c50=”

    },

     "diskUsage": {"total": 4096, "used": 1024, "free" 3072},

     "state": "online",

}
DELETE /rhfsServices/id

Use the DELETE /rhfsServices/{id} request to unmanage an remote host file sync Services, This will remote host file sync Services from the database and it will no longer be associated with any resource.

#This will use different api to run the service
````
[1]-Python-2.7
[3]-Flask-PyMongo-0.5.1
[4]-Flask-restplus-0.10.1


1. Remote host file sync Service requirements includes
````
    flask-restplus==0.10.1
    Flask-PyMongo==0.3.0
    Flask-RESTful==0.2.12
    Flask == 0.11
    Jinja2==2.7.3
    MarkupSafe==0.23
    Werkzeug==0.9.6
    aniso8601==0.82
    gunicorn==19.0.0
    itsdangerous==0.24
    pytz==2014.4
    six==1.7.2
````
 #Once clone is complete the remote host file sync Services  tree will look like this:
 ````

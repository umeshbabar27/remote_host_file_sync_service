import logging
import traceback
import datetime
import paramiko
import subprocess
import os
import shlex
import uuid
import random
from flask import Response
from bson import json_util, ObjectId
from flask import request, jsonify, json, app, current_app
from flask_restplus import Resource, Api, fields
from pymongo.errors import ConnectionFailure, OperationFailure

from remote_host_file_sync_service import config
from remote_host_file_sync_service.api import mongo_data
from remote_host_file_sync_service import api
from multiprocessing.pool import ThreadPool
from time import time as timer
import urllib3
from pylxca import *


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
log = logging.getLogger(__name__)

api = Api(version='1.0', title='Remote host file sync Service', description='Remote host file sync Service')

@api.errorhandler
def database_not_found_error_handler(e):
    log.error(traceback.format_exc())
    return {'message': 'A database result was required but none was found.'}, 404


@api.errorhandler
def default_error_handler(e):
    message = 'An unhandled exception occurred.'
    log.error(message)

    if not config.FLASK_DEBUG:
        return {'message': message}, 500


rhfsServices_post = api.model('rhfsServices post', {
    'address': fields.String(required=True, description='The unique address'),
    'description' : fields.String(required=False, description='The address description'),
    'state': fields.String(required=False, description='The state will show online or offline'),
})


updateStatusTask_post=api.model('updateStatusTask post', {
    'type': fields.String(required=True, description='The unique type'),
    'ids': fields.List(fields.String(required=True, description='updateStatusTask, contains list of server ids')),
})


@api.route('/services')
class RhfsService(Resource):

    @api.response(400, 'Invalid ID supplied')
    @api.response(404, 'rhfsService not found')
    def get(self, id=None):  # get_rhfsService_by_id or get_all_rhfsService
        if id is None:
            try:
                log.debug('getting all rhfsServices---')
                docs = mongo_data.db.rhfsService.find()
                data = [json.loads(json.dumps(format_object_id(item), default=json_util.default)) for item in docs]
                if data:
                    log.debug('rhfsService found from the database--')
                    return jsonify(data)
                else:
                    log.debug('no any rhfsService found in the database')
                    return jsonify(data)
            except Exception as e:
                log.error(e.message)
                return e.message
        else:
            try:
                log.debug('getting single rhfsService against id - %s', id)
                docs = mongo_data.db.rhfsService.find({"_id": ObjectId(id)})
                data = [json.loads(json.dumps(format_object_id(item), default=json_util.default)) for item in docs]
                if data:
                    log.debug('rhfsService found from the database--',)
                    return jsonify(data)  # 'get rhfsService by id' #
                else:
                    log.debug('no any rhfsService found in the database')
                    return responses.get('rhfsService_not_found'), 404
            except Exception as e:
                log.error(e.message)
                return e.message

    @api.response(201, 'rhfsService successfully created.')
    @api.expect(rhfsServices_post)
    def post(self):  # request to manage (create) a new rhfsService.
        log.debug('post call request to manage (create) a new rhfsService')
        if request.is_json:
            data = request.get_json()
            log.debug('getting json data from request--')
            if validate_json(request):
                try:
                    username = 'XXXX'
                    password = 'XXXX'
                    pub_key = data['publicKey']['key']
                    server = data['address']
                    log.debug('trying to deploy key to the target.....')
                    if deploy_key(pub_key, server, username, password):
                        if run_lsyncd(server):
                            log.debug('success for run lsyncd to the target  server.....')
                            log.debug('manage (create) a new  service using valid request data--')
                            obj_id=mongo_data.db.rhfsService.insert(data)  #'manage (create) a new  service'
                            docs = mongo_data.db.rhfsService.find({"_id": ObjectId(obj_id)})
                            rhfsService_obj = [json.loads(json.dumps(format_object_id(item), default=json_util.default)) for item in
                                        docs]
                            log.debug('Service successfully created against id - %s', obj_id)
                            response = responses.get('Service_create_success'), 201
                            #response.status_code = 201
                            #response.headers['location'] = 'remote/services/' + str(obj_id)
                            #response.autocorrect_location_header = False
                            return response
                        else:
                            log.debug('unable to push master pub key to the targeted service')
                            return responses.get('Service_manage_failure'), 400
                    else:
                        log.debug('unable to push master pub key to the targeted service')
                        return responses.get('Service_manage_failure'), 400
                except Exception as e:
                    log.error(e.message)
                    return e.message
            else:
                log.debug('incorrect or missing parameters')
                return responses.get('incorrect_or_missing_parameters'), 400
        else:
            log.debug('Request was not JSON')
            return responses.get('request_not_json'), 400

    @api.response(400, 'Invalid ID supplied')
    @api.response(404, 'Service not found')
    def delete(self, id, apiKey = None):  # delete Service
            try:
                log.debug('delete Service function start --')
                status=mongo_data.db.rhfsService.remove({"_id": ObjectId(id)})
                res=json.loads(json_util.dumps(status))
                if res["n"] == 1:
                    log.debug('Service successfully deleted with id - %s', id)
                    return responses.get('Service_delete_success')
                else:
                    log.debug('Service not found with id - %s', id)
                    return responses.get('service_not_found'), 404
            except Exception as e:
                log.error(e.message)
                return e.message


    @api.response(400, 'Invalid ID supplied')
    @api.response(404, 'Service not found')
    @api.response(405, 'Validation Exception')
    @api.response(200, 'Service successfully updated.')
    @api.expect(rhfsServices_post)
    def put(self, id):  # update rhfsService
        log.debug('update existing Service function start --')
        if request.is_json:
            data = request.get_json()
            log.debug('getting Service id - %s with data - %s', id, data)
            if validate_json(request):
                try:
                    username = 'XXXX'
                    password = 'XXXX'
                    pub_key = data['publicKey']['key']
                    server = data['address']
                    log.debug('trying to deploy key to the target.....')
                    if deploy_key(pub_key, server, username, password):
                        if run_lsyncd(server):
                            res=mongo_data.db.rhfsService.update({"_id": ObjectId(id)},{"$set":data})  #return 'update '
                            if res["updatedExisting"] is True:
                                log.debug('Service updated successfully')
                                return responses.get('Service_modify_success'),200
                            else:
                                return responses.get('Service_not_found'), 404
                        else:
                            log.debug('unable to push master pub key to the targeted service')
                            return responses.get('Service_manage_failure'), 400
                    else:
                        log.debug('unable to push master pub key to the targeted service')
                        return responses.get('Service_manage_failure'), 400
                except Exception as e:
                    log.error(e.message)
                    return e.message
            else:
                log.debug('incorrect or missing parameters')
                return responses.get('incorrect_or_missing_parameters'), 400
        else:
            return responses.get('request_not_json'), 400


api.add_resource(RhfsService, '/services', methods=['GET', 'POST'])
api.add_resource(RhfsService, '/services/', methods=['GET', 'POST'])
api.add_resource(RhfsService, '/services/<id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
api.add_resource(RhfsService, '/services/<id>/', methods=['GET', 'PATCH', 'PUT', 'DELETE'])


@api.route('/services/statusUpdateTask')
class StatusUpdateTask (Resource):
    #@api.response(200, 'Test connectivity job created.')
    @api.expect(updateStatusTask_post)
    def post(self):  # request to check test connectivity for servers.
        log.debug('post call request to check test connectivity for servers.')
        if request.is_json:
            data = request.get_json()
            log.debug('getting json data from request--')
            if data['ids'] and data['type'] == 'remoteServices':
                try:
                    server_ips = data['ids']
                    log.debug('checking test connectivity with the list of servers.....')
                    task_obj = run_threadpool(server_ips)
                    if task_obj:
                        log.debug('started test connectivity job successfully')
                        return json.loads(task_obj)
                    else:
                        log.debug('unable to start test connectivity job')
                        return responses.get('test_connectivity_failure'), 400
                except Exception as e:
                    log.error(e.message)
                    return e.message
            else:
                log.debug('incorrect or missing parameters')
                return responses.get('incorrect_or_missing_parameters'), 400
        else:
            log.debug('Request was not JSON')
            return responses.get('request_not_json'), 400


api.add_resource(StatusUpdateTask, '/services/statusUpdateTask', methods=['POST'])
api.add_resource(StatusUpdateTask, '/services/statusUpdateTask/', methods=['POST'])


@api.route('/managementServerPublicKey')
class SSHKeyOperations(Resource):

    @api.response(404, 'ssh key not found')
    def get(self):  # get ssh key
        try:
            data = {"key": get_ssh_key()}
            return jsonify(data)
        except Exception as e:
            log.error(e.message)
            return e.message


    @api.response(201, 'ssh key successfully generated.')
    def post(self):  # request to create a new ssh key
         try:
             log.debug('trying to generate ssh key and copy to ../resources')
             generate_ssh_key()#generating new ssh key
             message_resosnse = responses.get('generate_ssh_key_success')
             message_resosnse.update({'key': get_ssh_key()})
             return responses.get('generate_ssh_key_success'), 201
         except Exception as e:
             log.error(e.message)
             return e.message



api.add_resource(SSHKeyOperations, '/managementServerPublicKey', methods=['GET', 'POST'])
api.add_resource(SSHKeyOperations, '/managementServerPublicKey/', methods=['GET', 'POST'])


@api.route('/info')
class Info(Resource):
    @api.response(404, 'Data not found')
    def get(self):  # get info
            try:
                data = {}
                return jsonify(data)
            except Exception as e:
                log.error(e.message)
                return e.message


api.add_resource(Info, '/info', methods=['GET'])
api.add_resource(Info, '/info/', methods=['GET'])


@api.route('/health')
class Health(Resource):
    @api.response(404, 'Data not found')
    def get(self):  # get health
            try:
                data = {"description": "service Discovery Client","status": "UP"}
                return jsonify(data)
            except Exception as e:
                log.error(e.message)
                return e.message


api.add_resource(Health, '/health', methods=['GET'])
api.add_resource(Health, '/health/', methods=['GET'])


# validate the json input data
def validate_json(req_obj):
    data = req_obj.get_json()
    valid_algorithm = ['ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521', 'ssh-rsa', 'ssh-dss']
    if 'address' in req_obj.json and 'publicKey' in req_obj.json and 'resourceGroups' in req_obj.json:
        if data['resourceGroups']and 'algorithm' in data['publicKey'] and 'key' in data['publicKey']:
            if data['publicKey']['algorithm'] not in valid_algorithm:
                return False   #responses.get('incorrect_or_missing_algorithm'), 400
            else:
                return True
    else:
        return False


# run multi thread to check connectivity
def run_threadpool(server_ips):
    remote_server_count.set_remote_server_count(len(server_ips))
    increase_percentage.set_increase_percentage(100 / len(server_ips))
    resp = '{"customUid": "'+uuid.uuid4().hex.upper()+'",  "uid": "'+random.randint(0, 100)+'" }'
    for _id in json.loads(resp): jb_id = _id['uid']
    job_id.set_job_id(jb_id)
    results = []
    ips_context_list=[]
    app = current_app._get_current_object()
    for ip in server_ips:
        ips_context_list.append([ip,app])
    ThreadPool().map_async(test_connectivity, ips_context_list,  callback=results.extend)
    return resp


# check test connectivity with target servers
def test_connectivity(ips_context_list):
    ip = ips_context_list[0]
    new_app = ips_context_list[1]
    log.debug('Inside test connectivity function- %s', ip)
    cmd_output = None
    try:
        cmd_output = subprocess.check_output(['ssh root@"%s" df -m /data' % ip], shell=True)
    except subprocess.CalledProcessError as e:
        cmd_output = e.output
    df_array = [shlex.split(x) for x in
                cmd_output.rstrip().split('\n')]
    df_num_lines = df_array[:].__len__()

    df_json = {}
    df_json["filesystems"] = []
    for row in range(1, df_num_lines):
        df_json["filesystems"].append(df_to_json(df_array[row]))
    json_data = json.loads(json.dumps(df_json, sort_keys=True, indent=2))

    #updating task with updated percentage
    incr_percentage = increase_percentage.get_increase_percentage()
    update_tasks_job(incr_percentage)

    #updaing test connectivity to the database
    update_testConnectivityData_to_db(new_app,ip, json_data)


def update_tasks_job(increase_percentage_by):
    log.debug('update_tasks_job data fuction start----------')
    jobs_id=job_id.get_job_id()
    job_percentage.set_job_percentage(job_percentage.get_job_percentage()+increase_percentage_by)
    updated_percentage = job_percentage.get_job_percentage()
    if remote_server_count.get_remote_server_count()==1:
        complet_task_data = '[{"jobUID":"' + str(job_id) + '","jobState":"Complete"}]'
        log.debug('Update job id- %s status code-%s', job_id, complet_task_data)
    else:
        update_tsk_data = '[{"jobUID":"' + str(jobs_id) + '","percentage": ' + str(updated_percentage) + '}]'
        log.debug('started Update job with id- %s and status code-%s', jobs_id, update_tsk_data)


# update test connectivity data against ip
def update_testConnectivityData_to_db(new_app, ip, json_obj):
    try:
        with new_app.app_context():
            log.debug('updating update_testConnectivityData_to_db start with ip--------- %s', ip)
            log.debug('updating test connectivity data for - %s - %s', ip,json_obj ['filesystems'])
            if json_obj['filesystems']:
                for key in json_obj['filesystems']:
                    free = key['filesystem']['available']
                    used = key['filesystem']['used']
                    total = key['filesystem']['size']
                res = mongo_data.db.rhfsService.update({'address': ip}, {"$set": {"diskUsage": {"total": total, "used": used, "free": free},'state': 'online'}})
                if res["updatedExisting"] is True:
                    log.debug('test connectivity status updated as online successfully------')
            elif not json_obj['filesystems']:
                res = mongo_data.db.rhfsService.update({'address': ip}, {"$set": {'state': 'offline'}})
                if res["updatedExisting"] is True:
                    log.debug('test connectivity status updated as offline successfully------')
            else:
                log.debug('test connectivity status update failed')
    except Exception as e:
        log.error(e.message)
        return e.message


# convert df command raw output to json object
def df_to_json(tokenList):
    result = {}
    fsName = tokenList[0]
    fsSize = tokenList[1]
    fsUsed = tokenList[2]
    fsavailable = tokenList[3]
    fsMountPoint = tokenList[5]
    result["filesystem"] = {}
    result["filesystem"]["name"] = fsName
    result["filesystem"]["size"] = fsSize
    result["filesystem"]["used"] = fsUsed
    result["filesystem"]["available"] = fsavailable

    result["filesystem"]["mount_point"] = fsMountPoint
    return result


# set and get job percentage for test connectivity
class Job_percentage:
    def __init__(self, job_percentage=0):
        self.job_percentage = job_percentage

        # getter method

    def get_job_percentage(self):
        return self.job_percentage

        # setter method

    def set_job_percentage(self, job_percentage):
        self.job_percentage = job_percentage


job_percentage = Job_percentage()


# set and get remote_server_count for test connectivity
class Remote_server_count:
    def __init__(self, remote_server_count=0):
        self.remote_server_count = remote_server_count

        # getter method

    def get_remote_server_count(self):
        self.remote_server_count=self.remote_server_count-1
        return self.remote_server_count

        # setter method

    def set_remote_server_count(self, remote_server_count):
        self.remote_server_count = remote_server_count


remote_server_count = Remote_server_count()

# set and get increase_percentage for test connectivity
class Increase_percentage:
    def __init__(self, increase_percentage=0):
        self.increase_percentage = increase_percentage

        # getter method

    def get_increase_percentage(self):
        return self.increase_percentage

        # setter method

    def set_increase_percentage(self, increase_percentage):
        self.increase_percentage = increase_percentage


increase_percentage = Increase_percentage()


# set and get job id for new jab
class Job_id:
    def __init__(self, Job_id=0):
        self.Job_id = Job_id

        # getter method

    def get_job_id(self):
        return self.Job_id

        # setter method

    def set_job_id(self, Job_id):
        self.Job_id = Job_id


job_id = Job_id()


# get existing key from '/opt/id_rsa.pub'
def get_ssh_key():
    try:
        if os.path.exists('/opt/id_rsa.pub'):#rsa pub key location
            log.debug('getting ssh key to display--')
            ssh_key = open(os.path.expanduser('/opt/id_rsa.pub')).read()
            data = ssh_key.rstrip()
            return data
        else:
            log.debug('No ssh key found,Please try to generate new ssh key')
            return responses.get('get_ssh_key_failure'), 500
    except Exception as e:
        log.error(e.message)
        return e.message

# generate ssh key by using .sh file
def generate_ssh_key():
    try:
        if os.path.exists('/home/root/serviceSSHKey.sh'):
            log.debug('generating new ssh key to display--')
            subprocess.check_output('/home/root/serviceSSHKey.sh %s %s %s' % ('root', '1', '0'), shell=True)
        else:
            log.debug('Unable to generate new ssh key')
            return responses.get('get_ssh_key_failure'), 500
    except Exception as e:
        log.error(e.message)
        return e.message


# config ssh pub key from master to service
def deploy_key(key, server, username, password):
    # First push target service pub-key to master
    try:
        if not os.path.exists('/home/root/.ssh/id_rsa.pub'):
            #subprocess.check_output("ssh-keygen -f ~/.ssh/id_rsa -t rsa -N ''", shell=True)
            generate_ssh_key()
            subprocess.check_output('touch ~/.ssh/known_hosts', shell=True)
            subprocess.check_output('touch ~/.ssh/authorized_keys', shell=True)

        key = server + ' ' + key
        subprocess.check_output('echo %s >> ~/.ssh/known_hosts' % key, shell=True)
        subprocess.check_output('echo %s >> ~/.ssh/authorized_keys' % key, shell=True)

        # Then get master pub-key to push to the target service
        master_key = open(os.path.expanduser('~/.ssh/id_rsa.pub')).read()

        #create paramiko client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # no known_hosts error
        log.debug("Trying to connect the targeted service ...........")

        client.connect(server, username=username, password=password, allow_agent=False,look_for_keys=False)
        #client.connect(server, username=username, allow_agent=False, look_for_keys=True)
        if True:
            log.debug("the targeted service connection successful -----------------")
            client.exec_command('mkdir -p ~/.ssh/')
            client.exec_command('echo "%s" > ~/.ssh/authorized_keys' % master_key)
            client.exec_command('chmod 644 ~/.ssh/authorized_keys')
            client.exec_command('chmod 700 ~/.ssh/')
            client.close()
            return True
        else:
            log.debug("unable to connect the targeted service -----------------")
            return False
    except Exception as e:
        log.error(e.message)
        return False


def run_lsyncd(target_ip):
    # run lsyncd to enable lsyncd with target server
    try:
        if os.path.exists('/home/root/lsyncd.conf'):
            log.debug("started run lsyncd for targeted  server -----------------")
            cmd1 = 'sed -i "s/host.*/host = \\"%s\\",/g" /home/root/lsyncd.conf' %(target_ip)
            cmd2 = 'lsyncd -log all /home/root/lsyncd.conf'
            subprocess.check_output(cmd1 + " && " + cmd2, shell=True)
            return True
        else:
            log.debug('Unable to run lsyncd--')
            return False
    except (subprocess.CalledProcessError, Exception) as e:
        log.error(e.message)
        return False


# format and parse objectId to split and use only id
def format_object_id(item):
    if item.get('_id'):
        item['id'] = str(item.get('_id'))
        del item['_id']
        return item
    else:
        return item


#All responses
responses = {
    'Service_create_success':{
  "result": "success",
  "messages": [
    {
      "id": "FQXHMSE0001I",
      "text": "The request completed successfully.",
      "recovery": {
        "text": "Information only. No action is required.",
        "URL": ""
},
      "explanation": ""
}
  ]
},

'generate_ssh_key_success':{
   "result": "success",
   "messages": [{
      "id": "FQXHMSE0001I",
      "text": "The request completed successfully.",
      "explanation": "",
      "recovery": {
         "URL": "",
         "text": "Information only. No action is required."
      }
   }]
}
,



  'get_ssh_key_failure':{
  "result": "failure",
  "messages": [
    {
      "id": "FQXHMSE0001I",
      "text": "Internal server error. An internal error occurred, No ssh key found, Please try to generate new ssh key.",
      "recovery": {
        "text": "Internal server error. An internal error occurred, No ssh key found, Please try to generate new ssh key.",
        "URL": ""
},
      "explanation": ""
}
  ]
}
    ,

    'Service_not_found': {"result":"failure","messages":[{"id":"FQXHMSE0291J","text":"The request could not be completed successfully.","recovery":{"text":"Service not found","URL":""},"explanation":"Service not found."}]},
    'Service_modify_success': {
  "result": "success",
  "messages": [
    {
      "id": "FQXHMSE0001I",
      "text": "The request to modify service completed successfully.",
      "recovery": {
        "text": "Information only. No action is required.",
        "URL": ""
},
      "explanation": ""
}
  ]
}
,
    'Service_manage_failure': {"result":"failure","messages":[{"id":"FQXHMSE0291J","text":"The request to log in could not be completed successfully.","recovery":{"text":"You must log in using the correct user name and password. If you do not know the correct password, ask your system administrator to reset your password on the authentication server.","URL":""},"explanation":"The user name or password is not valid."}]},
        'Service_delete_success': {
  "result": "success",
  "messages": [
    {
      "id": "FQXHMSE0001I",
      "text": "The request to delete service completed successfully.",
      "recovery": {
        "text": "Information only. No action is required.",
        "URL": ""
},
      "explanation": ""
}
  ]
}
,
    'incorrect_or_missing_parameters':{"result":"failure","messages":[{"id":"FQXHMSE0291J","text":"The request could not be completed successfully due to incorrect or missing parameters","recovery":{"text":"please add correct parameters","URL":""},"explanation":"incorrect or missing parameters."}]},
    'incorrect_or_missing_algorithm':{'message':'algorithm should be similar value among - [ecdsa-sha2-nistp256, ecdsa-sha2-nistp384, ecdsa-sha2-nistp521, ssh-rsa, ssh-dss]'},
    'request_not_json':{'message':'Request was not JSON'},
    'similar_param_error':{'message':'Current Service has similar parameter values'}

}


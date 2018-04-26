from django.db import models
from django.http import JsonResponse
import requests
from datetime import datetime
import base64
import json
import sys
import time
import ssl
from urllib.request import urlopen
from rest_framework.response import Response
#from rest_framework import JSONField


class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)


class Rezdy(models.Model):
    data = models.TextField()
    key = models.CharField(max_length=50)
    url = models.URLField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)

    '''def __get__(self, instance, owner):
        return self.data, self.key

    def downloadmarket(self):
        response = requests.get(self.url, self.key)
        self.data = response
        print (response.json())
        return response

    def postmarket(self):
        post = requests.post()
        return post'''


def download(response):
    """
    Returns Rezdy Marketplace products
    """
    if response.method == 'GET':
        data = requests.get('https://api.rezdy.com/v1/products/marketplace?apiKey=1d7ce4142c634882846e3597aaef36e4')

    return Response(data.json(), safe=False)


class NutanixObj:
    def __init__(self, username, password, created=None):
        self.ip_addr = '10.14.8.10'
        self.username = username
        self.password = password
        self.created = created or datetime.now()
        self.rest_params_init()

    # Initialize REST API parameters
    def rest_params_init(self, sub_url="", method="",
                         body=None, content_type="application/json"):
        self.sub_url = sub_url
        self.body = body
        self.method = method
        self.content_type = content_type

    # Create a REST client session.
    def rest_call(self):
        base_url = 'https://%s:9440/PrismGateway/services/rest/v2.0/%s' % (
            self.ip_addr, self.sub_url)
        if self.body and self.content_type == "application/json":
            self.body = json.dumps(self.body)
        request = urlopen(base_url, data=self.body)
        base64string = base64.encodestring(
            '%s:%s' %
            (self.username, self.password)).replace(
            '\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)

        request.add_header(
            'Content-Type',
            '%s; charset=utf-8' %
            self.content_type)
        request.get_method = lambda: self.method

        try:
            if sys.version_info >= (2, 7, 9):
                ssl_context = ssl._create_unverified_context()
                response = urlopen(request, context=ssl_context)
            else:
                response = urlopen(request)
            result = response.read()
            if result:
                result = json.loads(result)
            return response.code, result
        except urllib.HTTPError as e:
            err_result = e.read()
            if err_result:
                try:
                    err_result = json.loads(err_result)
                except:
                    print ('Error: %s' % e)
                    return "408", None
            return "408", err_result
        except Exception as e:
            print ("Error: %s") % e
            return "408", None

        """try:
            response = urllib2.urlopen(request)
            result = response.read()
            if result:
                result = json.loads(result)
            return response.code, result
        except urllib2.HTTPError as e:
            err_result = e.read()
            if err_result:
                try:
                    err_result = json.loads(err_result)
                except:
                    print "Error: %s" % e
                    return "408", None
            return "408", err_result
        except Exception as e:
            print "Error: %s" % e
            return "408", None
            """


class ApiLibrary:
    def __init__(self):
        pass

    # Parse a list
    # list to parse
    # key for which parse is to be done
    def parse_list(self, toparse, lookfor):
        for data in toparse:
            if isinstance(data, dict):
                return data.get(lookfor)

    # Parse a complex dictionary.
    # result : dictionary to parse
    # meta_key : the key which has sub key for which parse is being done.
    # look_for: the key for which parse is to be done.
    def parse_result(self, result, meta_key, lookfor):
        uuid = None
        if result:
            for key in result:
                if key == meta_key:
                    if isinstance(result[key], list):
                        uuid = self.parse_list(result[key], lookfor)
                        return uuid
                    else:
                        if type(result[key]) == dict:
                            return result[key].get(lookfor, None)
                        return result[key]
                elif isinstance(result[key], dict):
                    uuid = self.parse_result(result[key], meta_key, lookfor)
                    if uuid:
                        return uuid
        return uuid

    # Check the return status of API executed
    def check_api_status(self, status, result):
        if result:
            return self.parse_result(result, "status", "state")
        else:
            return None

    def print_failure_status(self, result):
        if result:
            status = result.get('status')
            if status:
                print ('*' * 80)
                state = self.parse_result(result, "status", "state")
                if state == "kError":
                    print ("Reason: ", status.get('reason'))
                    print ("Message: ", status.get("message"))
                else:
                    print ("Reason: ", result.get('reason'))
                    print ("Details: ", result.get('details'))
                    print ("Message: ", result.get("message"))

    def __is_result_complete(self, testRestApi, task_uuid, get_task):
        (status, result) = get_task(testRestApi, task_uuid)
        if result and str(status) == "200":
            percent_complete = result.get('percentage_complete')
            progress_status = result.get('progress_status')
            if str(percent_complete) == "100" and progress_status == "SUCCESS":
                return result.get('parent_task_uuid')
        return None

    def track_completion_status(
            self, testRestApi, status, result, api_uuid, get_task):
        retry_count = 5
        wait_time = 2  # seconds
        task_uuid = None
        count = 0
        uuid = None
        if str(status) == "201":
            print ("Already exists")
            return
        if result and str(status) == "200":
            uuid = result.get(api_uuid, None)
            print (uuid)
            if not uuid:
                task_uuid = result.get('task_uuid', None)
                print (task_uuid)
            else:
                return uuid
        while count < retry_count and not uuid:
            count = count + 1
            time.sleep(wait_time)
            uuid = self.__is_result_complete(testRestApi, task_uuid, get_task)
        if not uuid:
            print ("Error detail:", self.parse_result(result, "meta_response", "error_detail"))
            return None
        return uuid

# Get Cluster info based on uuid.
def get_cluster(testRestApi, cluster_uuid):
    sub_url = 'clusters/%s' % cluster_uuid
    testRestApi.rest_params_init(sub_url=sub_url, method="GET")
    (status, result) = testRestApi.rest_call()
    return status, result


# Get the list of clusters.
def get_clusters(testRestApi):
    testRestApi.rest_params_init(
        sub_url="clusters",
        method="GET")
    (status, result) = testRestApi.rest_call()
    return status, result


def NutanixBegin(username, password):
    cluster_uuid = None
    testRestApi = NutanixObj(username, password)
    api_library = ApiLibrary()

    # Get Clusters by the provided filters.
    (status, cluster_list) = get_clusters(testRestApi)
    if str(status) == "200":
        clusters = cluster_list.get('entities')
        for cluster in clusters:
            cluster_uuid = cluster.get('cluster_uuid')
            print ("Cluster UUID:", cluster_uuid)
    else:
        print ("Failed to get clusters using filters")
        api_library.print_failure_status(cluster_list)
        print ('*' * 80)
        return

    # Get a cluster by the giveen uuid.
    (status, result) = get_cluster(testRestApi, cluster_uuid)
    if str(status) == "200":
        print ('*' * 80)
        print ("Cluster Details with uuid", cluster_uuid)
        print ('*' * 80)
        pp.pprint(result)
        print ('*' * 80)
    else:
        print ("Failed to get clusters using filters")
        api_library.print_failure_status(result)
        print ('*' * 80)
        return

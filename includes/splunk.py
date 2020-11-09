import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from xml.dom import minidom
import time
import json
from pathlib import Path

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class splunkClass():
    host = str()
    port = int()
    session = str()

    def __init__(self,host,port,username,password,secure=False,ca=None,requestTimeout=30):
        self.host = host
        self.port = port
        self.secure = secure
        self.requestTimeout = requestTimeout
        self.ca = None
        if ca:
            if ca != "None":
                self.ca = Path(ca)
            else:
                self.ca = "None"
        else:
            self.ca = None
        if not self.authenticate(username,password):
            return None

    def apiCall(self,methord,uri,data=None):
        response = None
        headers = None
        if "headers" in self.__dict__:
            headers = self.headers
        try:
            if self.ca:
                if self.ca != "None":
                    if methord == "POST":
                        response = requests.post("{0}{1}".format(self.url,uri),headers=headers,data=data,verify=self.ca,timeout=self.requestTimeout)
                    elif methord == "GET":
                        response = requests.get("{0}{1}".format(self.url,uri),headers=headers,verify=self.ca,timeout=self.requestTimeout)
                else:
                    if methord == "POST":
                        response = requests.post("{0}{1}".format(self.url,uri),headers=headers,data=data,verify=False,timeout=self.requestTimeout)
                    elif methord == "GET":
                        response = requests.get("{0}{1}".format(self.url,uri),headers=headers,verify=False,timeout=self.requestTimeout)
            else:
                if methord == "POST":
                    response = requests.post("{0}{1}".format(self.url,uri),headers=headers,data=data,timeout=self.requestTimeout)
                elif methord == "GET":
                    response = requests.post("{0}{1}".format(self.url,uri),headers=headers,timeout=self.requestTimeout)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            pass
        return response

    def authenticate(self, username, password):
        httpScheme = "http"
        if self.secure:
            httpScheme = "https"
        self.url = "{0}://{1}:{2}".format(httpScheme,self.host,self.port)
        response = self.apiCall("POST","/services/auth/login",data={ "username" : username, "password" : password })
        if response.status_code == 200:
            session = minidom.parseString(response.text).getElementsByTagName('sessionKey')[0].childNodes[0].nodeValue
            self.headers = { "Authorization" : "{0} {1}".format("Bearer",session) }
        
    def startJob(self,searchQuery):
        response = self.apiCall("POST","/services/search/jobs",data={ "search" : searchQuery })
        if response.status_code == 201:
            return minidom.parseString(response.text).getElementsByTagName('sid')[0].childNodes[0].nodeValue

    def waitJob(self,jobID,maxLoops=10):
        done = False
        loop = 0
        while not done:
            if loop > maxLoops:
                return False
            response = self.apiCall("GET","/services/search/jobs/{0}/".format(jobID))
            if response.status_code == 200:
                keys = minidom.parseString(response.text).getElementsByTagName('content')[0].childNodes[1].childNodes
                for key in keys:
                    try:
                        if key._attrs["name"].nodeValue == "isDone":
                            if key.childNodes[0].nodeValue == "1":
                                done = True
                                break
                    except:
                        pass
                pass
            else:
                return False
            loop+=1
            time.sleep(0.5)
        return True


    def getJob(self,jobID):
        response = self.apiCall("GET","/services/search/jobs/{0}/results/?output_mode=json".format(jobID))
        if response.status_code == 200:
            return json.loads(response.text)


from plugins.splunk.includes import splunk

from core.models import trigger

from core import logging, auth, db, helpers

class _splunkSearch(trigger._trigger):
    splunkJob = str()
    splunkHost = str()
    splunkPort = int()
    splunkUsername = str()
    splunkPassword = str()
    insecure = bool()
    searchQuery = str()
    ca = str()

    def check(self):
        password = auth.getPasswordFromENC(self.splunkPassword)
        secure = not self.insecure
        s = splunk.splunkClass(self.splunkHost,self.splunkPort,self.splunkUsername,password,secure=secure,ca=self.ca)
        if not s:
            if logging.debugEnabled:
                logging.debug("Unable to authenticate to Splunk instance. actionID={0}".format(self._id),1)
            return
        jobID = s.startJob(self.searchQuery)
        if s.waitJob(jobID):
            pollResult = s.getJob(jobID)
            self.result["events"] = pollResult["results"]

    def setAttribute(self,attr,value,sessionData=None):
        if attr == "splunkPassword" and not value.startswith("ENC "):
            if db.fieldACLAccess(sessionData,self.acl,attr,accessType="write"):
                self.splunkPassword = "ENC {0}".format(auth.getENCFromPassword(value))
                return True
            return False
        return super(_splunkSearch, self).setAttribute(attr,value,sessionData)
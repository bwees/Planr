from uuid import uuid1
from enum import Enum

class Status:
    notStarted = "Not Started"
    inProgress = "In Progress"
    complete = "Complete"

def assignmentFromDictionary(dictionaryForm):

    assignmentName = dictionaryForm["assignmentName"]
    className = dictionaryForm["className"]
    typeName = dictionaryForm["typeName"]
    dueDate = dictionaryForm["dueDate"]
    attachments = dictionaryForm["attachments"]
    notes = dictionaryForm["notes"]
    duration = dictionaryForm["duration"]
    uuid = dictionaryForm["uuid"]
    status = dictionaryForm["status"]

    return Assignment(assignmentName, className, typeName, dueDate, notes, duration, attachments=attachments, uuid=uuid, status=status)


def freeTimeFromDictionary(dictionaryForm):

    name = dictionaryForm["name"]
    duration = dictionaryForm["duration"]
    time = dictionaryForm["time"]
    uuid = dictionaryForm["uuid"]
    

    return freeTime(name, duration, time, uuid)

class freeTime(object):
    def __init__(self, name, duration, time, uuid=uuid1().hex):
        self.name = name
        self.duration = duration
        self.time = time
        self.uuid = uuid

    def dictionary(self):

        dictionaryForm = {}

        dictionaryForm["name"] = self.name
        dictionaryForm["duration"] = self.duration
        dictionaryForm["time"] = self.time
        dictionaryForm["uuid"] = self.uuid
        
        return dictionaryForm

class Assignment(object):
    def __init__(self, assignmentName, className, typeName, dueDate, notes, duration, attachments = [], status=Status.notStarted, uuid=uuid1().hex):
        self.assignmentName = assignmentName
        self.className = className
        self.typeName = typeName
        self.dueDate = dueDate
        self.attachments = attachments
        self.notes = notes
        self.duration = duration
        self.status = status
        self.uuid = uuid

    def __eq__(self, other):
        return self.uuid == other.uuid

    def saveAttachment(self, file):
        file.save("/attachments/" + self.uuid + "/"+ uuid1().hex)

    def dictionary(self):

        dictionaryForm = {}

        dictionaryForm["assignmentName"] = self.assignmentName
        dictionaryForm["className"] = self.className
        dictionaryForm["typeName"] = self.typeName
        dictionaryForm["dueDate"] = self.dueDate
        dictionaryForm["attachments"] = self.attachments 
        dictionaryForm["notes"] = self.notes
        dictionaryForm["status"] = self.status
        dictionaryForm["duration"] = self.duration
        dictionaryForm["uuid"] = self.uuid

        return dictionaryForm

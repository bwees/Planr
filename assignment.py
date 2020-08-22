from uuid import uuid1
from enum import Enum

class Status:
    notStarted = 0
    inProgress = 1
    complete = 2

class Assignment:
    def __init__(self, assignmentName, className, typeName, dueDate, notes, duration, attachments = [], status=Status.notStarted, uuid=uuid1()):
        self.assignmentName = assignmentName
        self.className = className
        self.typeName = typeName
        self.dueDate = dueDate
        self.attachments = attachments
        self.notes = notes
        self.duration = duration

        self.uuid = uuid.hex

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
        dictionaryForm["duration"] = self.duration
        dictionaryForm["uuid"] = self.uuid

        return dictionaryForm

import functions_framework
from clorm import monkey

monkey.patch()
import clingo
from google.cloud import storage
import os
import json
from clorm import ConstantStr,FactBase, StringField, ContextBuilder, Predicate, ConstantField,ph1_
cb = ContextBuilder
ASP_PROGRAM= r"/tasksUsers.lp"
class DayVals(Predicate):
    mon:bool
    tue:bool
    wed:bool
    thu:bool 
    fri:bool
    sat:bool
    sun:bool

class User(Predicate):
    name:ConstantStr
    userID:int
    avaliable:DayVals

class AssignDays(Predicate):
    user:User

class Task(Predicate):
    name:ConstantStr
    duration:int

class Assignment(Predicate):
    taskValue:ConstantStr
    user:ConstantStr
    duration:int
    avaliable:DayVals
    time:int
# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def clormTimetable(cloud_event):
    # def readBucket(fileName, bucketName):
    #     storageClient=storage.Client()
    #     bucketBlob=storageClient.bucket(bucketName)
    #     blob=bucketBlob.blob(fileName)
    #     userData=blob.download_as_bytes().decode("utf8")
    #     userVals = json.loads(userData)
    #     numberHive=userVals['numMember']
    #     print(userVals)
    #     return numberHive
    
    # jsonData=json.loads(contentString)
    currentMembers=0
    #Gain basic info on the file that was just added
    data = cloud_event.data
    event_id = cloud_event["id"]
    event_type = cloud_event["type"]
    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]
    storageClient=storage.Client()
    bucketVal=storageClient.bucket(bucket)
    blob=bucketVal.blob(name)
    userData=blob.download_as_bytes().decode("utf8")
    print(userData)
    try:
        userJson= json.loads(userVals)
        print(userJson)
    except e:
        print("PLEASEEE WHYYYY "+e)


    #Load in the contents of the json file

    
    for blob in storageClient.list_blobs(bucket,prefix=name):
        currentMembers+=1
    print(currentMembers)
    
    
    # ctrl=clingo.Control(unifier =[User, Task,Assignment])
    # ctrl.load(ASP_PROGRAM)
    

    # users=[User(name=userValues['name'],userID=userValues['userID'],avaliable=DayVals(mon=userValues['Mon'],tue=userValues['Tue'],wed=userValues['Wed'],thu=userValues['Thur'],fri=userValues['Fri'],sat=userValues['Sat'],sun=userValues['Sun'])) for userValues in userDetails['userSpecifications']]
    # tasks=[Task(name=taskValues['taskName'],duration=taskValues['duration'])for taskValues in taskDetails["TaskValues"][0]["TaskDescriptions"]]  
    # instances=FactBase(users+tasks)
    # print(instances)

    # ctrl.add_facts(instances)
    # ctrl.ground([("base", [])])

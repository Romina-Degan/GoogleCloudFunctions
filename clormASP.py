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
    userData=blob.download_as_bytes().decode()
    userVals=json.loads(userData)   
    maxMembers=userVals['numMember']
    
    for blob in storageClient.list_blobs(bucket,prefix=userVals['hiveID']):
        currentMembers+=1
    print(currentMembers)
    if maxMembers==currentMembers:
        print("all Members present")
        
        
    else:
        print("Not all Members are present so timetable wont be made") 
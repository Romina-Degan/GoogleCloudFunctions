import functions_framework
from clorm import monkey

monkey.patch()
import clingo
from google.cloud import storage
import os
import json
from clorm import ConstantStr,FactBase, StringField, ContextBuilder, Predicate, ConstantField,ph1_
cb = ContextBuilder
ASP_PROGRAM= "tasksUsers.lp"
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
    userID:ConstantStr
    #avaliable:DayVals

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
    def addToDict(name, userID):
        
        updateDict={
            "userID":userID,
            "name":name
        }
        return updateDict
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

    


    #Initalize the bucket again to access USER files in the storage 
    storageClient=storage.Client()
    bucketVal=storageClient.bucket(bucket)
    blob=bucketVal.blob(name)
    #Access the file contents in a way that the program can break down 
    userData=blob.download_as_bytes().decode()
    userVals=json.loads(userData)   
    maxMembers=userVals['numMember']
    allMembersDict ={"userSpecifications":[]}
    #Create a somewhat async function that depends on all members being present READ THE USER DOCUMENTS
    for blob in storageClient.list_blobs(bucket,prefix=userVals['hiveID']):      
        userData=blob.download_as_bytes().decode()
        userDictData=json.loads(userData)
        
        userDict=addToDict(userDictData['name'],userDictData['userID'])
        allMembersDict["userSpecifications"].append(userDict)
        # allMembersDict.update({'name':userDictData['name'], 'userID':userDictData['userID']})
        print(allMembersDict)
        currentMembers+=1
    print(allMembersDict)

    #If member is present call the ASP 
    if maxMembers==currentMembers:
        
        # for blobs in storageClient.list_blobs(bucket,prefix=userVals['hiveID']):
        #     # userVals[counter]={''}
        #     blobVal=bucketVal.blob(blobs.name)
        #     print(userDictData)
        #     userDictVals.update({'name':userDictData['name'], 'userID':userDictData['userID']})
            
        
        ctrl=clingo.Control(unifier=[User,Task,Assignment])
        ctrl.load(ASP_PROGRAM)
        users=[User(name=userValues['name'],userID=userValues['userID']) for userValues in allMembersDict['userSpecifications']]
        # users=[User(name=userValues['name'],userID=userValues['userID'], for userValues in userDetails['userSpecifications']]
        # tasks=[Task(name=taskValues['taskName'],duration=taskValues['duration'])for taskValues in taskDetails["TaskValues"][0]["TaskDescriptions"]]  
        #instances=FactBase(users+tasks)       
        print("all Members present")


        
    else:
        print("Not all Members are present so timetable wont be made") 
    
    # ctrl=clingo.Control(unifier =[User, Task,Assignment])
    # ctrl.load(ASP_PROGRAM)
    



    # ctrl.add_facts(instances)
    # ctrl.ground([("base", [])])



    # storageClient=storage.Client()
    # print(userData[3])
    # try:
    #     userJson= json.loads(userData)
    #     print(userJson)
    # except e:
    #     print("PLEASEEE WHYYYY "+e)

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
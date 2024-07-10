import functions_framework
from clorm import monkey

monkey.patch()
import clingo
from google.cloud import storage
import re
import json
from clorm import ConstantStr,FactBase, StringField, ContextBuilder, Predicate, ConstantField,ph1_
cb = ContextBuilder
ASP_PROGRAM= "tasksUsers.lp"
class AvaliableDays(Predicate):
    nameOfDay:str 

class User(Predicate):
    name:ConstantStr
    userID:ConstantStr
    minVal:int
    maxVal:int 

class PreferredTask(Predicate):
    name:ConstantStr
    duration:int
    user:ConstantStr
    taskID:int


class PreferredDays(Predicate):
    dateVal:int
    userID:ConstantStr

class Assignment(Predicate):
    taskValue:ConstantStr
    taskID:int
    user:ConstantStr
    userID:ConstantStr
    duration:int
    time:int
    date:int

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def clormTimetable(cloud_event):
    def addToUserDict(name, userID,minTime,maxTime,preferDays,preferTasks):
        
        updateDict={
            "userID":userID,
            "name":name,
            "minTime":minTime,
            "maxTime":maxTime,
            "preferDays":preferDays,
            "preferTasks":preferTasks
            
        }
        return updateDict
    def readTasks():
        storageClient= storage.Client()
        bucketVal=storageClient.bucket("asp-react")
        blob=bucketVal.blob("Task.json")
        taskData=blob.download_as_bytes().decode()
        taskDictData=json.loads(taskData)
        print(taskVals)
        return taskVals
    prefTask=[]
    userPrefTask={}
    personalVal="Personal"
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
        print(userDictData)
        userDict=addToUserDict(userDictData['name'],userDictData['userID'], userDictData['minTime'],userDictData['maxTime'],userDictData['preferDays'],userDictData['preferTasks'])
        allMembersDict["userSpecifications"].append(userDict)
        currentMembers+=1
    print(allMembersDict)
    blobTask= bucketVal.blob("Task.json")
    taskData=blobTask.download_as_bytes().decode()
    taskValuesJson=json.loads(taskData)

    #If member is present call the ASP 
    if maxMembers==currentMembers:
        ctrl=clingo.Control(unifier=[User,Assignment,PreferredTask,PreferredDays])
        ctrl.load(ASP_PROGRAM)
        users = [User(name=userValues['name'], userID=userValues['userID'], minVal=int(userValues['minTime']), maxVal=int(userValues['maxTime'])) for userValues in allMembersDict['userSpecifications']]
        #tasks=[Task(name=taskValues['taskName'],duration=taskValues['duration'])for taskValues in taskValuesJson["TaskValues"]]  
        instances=FactBase(users)
        ctrl.add_facts(instances)
        lastPref=[]
        for members in users:
            currTask=[] 
            currUser=(list(filter(lambda x:(x["userID"]==members.userID),allMembersDict['userSpecifications'])))
            currPref=currUser[0]['preferTasks']
            currDay=currUser[0]['preferDays']

            for days in currDay:
                instances.add(FactBase(PreferredDays(dateVal=days,userID=members.userID)))
                ctrl.add_facts(instances)
            prefTask={}
            currPref.append("Personal")
            for items in currPref:
                if items in lastPref and items!="Personal": 
                    currPref.remove(items)
            for items in currPref:
                for taskValues in  taskValuesJson["TaskValues"][0]["TaskDescriptions"]:        
                    if items in taskValues['label'] or taskValues['label']=="Personal":  
                        print(taskValues['label'])  
                        #NOTE TO SELF: REMEMBER FOR THIS THE CLASS FOR TASK THE ID IS SET TO INT SINCE JSON FILE IS INT BUT REAL IS STR                 
                        currTask=[PreferredTask(name=taskValues['taskName'],duration=taskValues['duration'] ,user=members.userID, taskID=taskValues['taskID'])]
                        instances.add(FactBase(currTask))
                        ctrl.add_facts(instances)
                lastPref.append(items)

        ctrl.ground([("base", [])])
        print(instances)
        solution=None
    
        def on_model(model):
            nonlocal solution
            solution=model.facts(unifier=[User,Assignment,PreferredTask,PreferredDays], atoms=True,raise_on_empty=True)

        ctrl.solve(on_model=on_model)
        if not solution:
            raise ValueError("No solution Found")

        query = solution.query(Assignment).where(Assignment.user == ph1_).order_by(Assignment.date, Assignment.time)
        results={}    
        print(users)
        for u in users: 
            print(u)
            assignments = list(query.bind(u.name ).all())
            userID=u.userID
            taskVals=[]
            if not assignments:
                print("User not assigned any tasks!".format(u.name))
                
            else:
                print("User {} assigned to: ".format(u.name))
                
                for a in assignments:
                    
                    print("\t chore {}, at time {} at date{}".format(a.taskValue,a.time,a.date))
                    taskVals.append({"TaskValue":a.taskValue, "time": a.time, "date ":a.date})

            results[str(userID)] = taskVals
            bhiveStorage=storage.Client()
            bhiveBucket= bhiveStorage.bucket("bhive-81306.appspot.com")
            bhiveBlob= bhiveBucket.blob("results/"+userVals['hiveID'])
            jsonResults= json.dumps(results,indent=4)
            bhiveBlob.upload_from_string(jsonResults)
        print("all Members present")
        
    else:
        print("Not all Members are present so timetable wont be made") 

#Requirements File
#functions-framework==3.*
#clorm 
#clingo
#google-cloud-storage
    

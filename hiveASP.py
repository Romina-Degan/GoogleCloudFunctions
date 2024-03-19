import functions_framework
import json
from google.cloud import storage
# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def userVals(cloud_event):
    def writeToASP(bucketName,vals, name):
        print(vals)
        storageClient=storage.Client()
        bucket=storageClient.bucket(bucketName)
        blob= bucket.blob(name)
        blob.content_type="application/json"
        
        with blob.open(mode="w") as f:
            f.write(vals)
        
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]
    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    print(f"Event ID: {event_id}")
    print(f"Event type: {event_type}")
    print(f"Bucket: {bucket}")
    print(f"File: {name}")
    print(f"Metageneration: {metageneration}")
    print(f"Created: {timeCreated}")
    print(f"Updated: {updated}")
    storageClient=storage.Client()
    bucket = storageClient.get_bucket(bucket)
    blob=bucket.blob(name)
    blobBytes=blob.download_as_bytes()
    blobString= blobBytes.decode("utf-8")
    writeToASP("asp_react",blobString,name)
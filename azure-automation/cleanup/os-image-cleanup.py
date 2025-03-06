import subprocess
import json
import os
from datetime import datetime, timezone

resource_group = os.environ.get('RESOURCE_GROUP')
gallery_name = os.environ.get('GALLERY_NAME')
gallery_image_definitions = os.environ.get('GALLERY_IMAGE_DEFINITIONS')

print (gallery_image_definitions," ",gallery_name," ",resource_group )
image_definitions = json.loads(gallery_image_definitions)

def is_old_date(publish_date_str):

  date_object = datetime.fromisoformat(publish_date_str)
  current_date = datetime.now(timezone.utc)

  days_difference = (current_date - date_object).days
  print('DAYS ',days_difference)

  return days_difference > 30

for image_defination in image_definitions:

  os_images_persisted=[]
  os_images_to_be_deleted=[]

  try:
    ## Run the command and capture the list of all the available versions
    command = f'az sig image-version list --gallery-image-definition {image_defination} --gallery-name {gallery_name} --resource-group {resource_group} --query "[].{{name:name, publish_date:publishingProfile.publishedDate, location:location, size:storageProfile.sizeInGb, tags:tags}}" --output json | jq "sort_by(.publish_date) | reverse"'
    os_image_json = subprocess.check_output(command, shell=True, universal_newlines=True)
    os_images = json.loads(os_image_json)

    # print('OUTPUTLINES',os_images)
    print('LENGTH OF LIST : ', len(os_images))
    sorted_images_sorted = sorted(os_images, key=lambda x: x['publish_date'], reverse=True)
    counter=0
    for os_image in sorted_images_sorted:
      # print('TAGS ',os_image['tags'])
      if counter<5 :
        os_images_persisted.append(os_image)
      elif os_image['tags'] and os_image['tags'].get('Persist') :
        os_images_persisted.append(os_image)
      else:
        if is_old_date(os_image['publish_date']):
          os_images_to_be_deleted.append(os_image)
        else:
          os_images_persisted.append(os_image)
          
      counter+=1
      
    print('Persisted Images: ')
    for persisted in os_images_persisted:
      print('OS Image persist version: ',persisted['name'])
      
    print('To be deleted Images: ')
    for deleted in os_images_to_be_deleted:
      print('OS Image persist version: ',deleted['name'])
      version=deleted['name']
      command = f'az sig image-version delete --gallery-image-definition {image_defination} --gallery-image-version {version} --gallery-name {gallery_name} --resource-group {resource_group}'
      subprocess.check_output(command, shell=True, universal_newlines=True)

  except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")
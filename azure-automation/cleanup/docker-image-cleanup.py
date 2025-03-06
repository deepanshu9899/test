import subprocess
import json
import os
from datetime import datetime, timezone

resource_group = os.environ.get('RESOURCE_GROUP')
container_registry = os.environ.get('CONTAINER_REGISTRY')

def is_old_date(publish_date_str):

  date_object = datetime.fromisoformat(publish_date_str)
  current_date = datetime.now(timezone.utc)

  days_difference = (current_date - date_object).days
  print('DAYS ',days_difference)

  return days_difference > 30

try:
  ## Get the list of all repositories
  command = f'az acr repository list --name {container_registry}'
  docker_repositories_list = json.loads(subprocess.check_output(command, shell=True, universal_newlines=True))
  print('Docker Images ',docker_repositories_list)
  print('LENGTH OF LIST : ', len(docker_repositories_list))
  
  for docker_repository in docker_repositories_list:
    print('Repository : ',docker_repository)

    ## Get all the tags of the Docker Repository
    command = f'az acr repository show-tags --name {container_registry} --repository {docker_repository} --orderby time_desc --detail'
    docker_tags_list = json.loads(subprocess.check_output(command, shell=True, universal_newlines=True))

    counter=0
    docker_tags_persisted=[]
    docker_tags_to_be_deleted=[]
    ## Apply logic to persist and delete the tags
    for docker_tag in docker_tags_list:

      ## Making a condition for <= because there is a 'latest' tag maintained by Azure itself
      if counter<=5 :
        docker_tags_persisted.append(docker_tag)
      else:
        if is_old_date(docker_tag['lastUpdateTime']):
          docker_tags_to_be_deleted.append(docker_tag)
        else:
          docker_tags_persisted.append(docker_tag)
      counter+=1
        
    print('Persisted Image Tags: ')
    for persisted in docker_tags_to_be_deleted:
      print('OS Image persist version: ',persisted['name'])
      
    print('To be deleted Images: ')
    for deleted in docker_tags_to_be_deleted:
      print('OS Image persist version: ',deleted['name'])
      version = deleted['name']
      # command = f'az acr repository delete --name {container_registry} --image {docker_repository}:{version} --yes'
      # subprocess.check_output(command, shell=True, universal_newlines=True)

except subprocess.CalledProcessError as e:
    print(f"Command failed with return code {e.returncode}")
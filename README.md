# Create venv if you want and use it
- `python -m venv venv`
- `source ./venv/bin/activate`

# To install ansible and tools
pip install -r requirements.txt

# To install all the roles and collections
- ansible-galaxy install -r ansible/requirements.yml
- pip install -r ~/.ansible/collections/ansible_collections/azure/azcollection/requirements-azure.txt

# Note
- Be ready with GUI access while installing xcode, as this step is time taking and might get stuck (ssh failure or any other reason). If xcode installation is taking too long, make sure to launch xocde through GUI and complete the first launch screen.

# Inventory file location
search "mac monterey inventory ansible" in 1pass, copy both the files(prod.yml, stage.yml) in "ansible/monterey/inventory" directory.

# Basic commands:
### scafold en empty role:
`ansible-galaxy role init <role name> --init-path  <path to role>`

Example:
```
ansible-galaxy role init exclude_ip --init-path  ansible/monterey/playbooks/roles/
```

### Run a playbook:
`ansible-playbook -i ansible/monterey/inventory/<inventory_filename> <path to playbook> --ask-pass -u ltuser -vvv`

Example:
```
ansible-playbook -i ansible/monterey/inventory/stage.yml ansible/monterey/playbooks/all.yml --ask-pass --ask-become-pass -u ltuser 
```

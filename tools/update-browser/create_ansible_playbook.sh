echo "
---
- name: Testing
  hosts: windows
  gather_facts: false

  tasks:
  - name: Install python libraries
    win_command: pip install requests

  - name: copy file
    win_copy:
      src: /home/runner/work/hyperexecute-devops/hyperexecute-devops$1
      dest: D:/

  - name: Run script
    win_command:
      argv:
        - python
        - D:\update_browsers.py
        - $2
        - $3
        - $4
  
  - name: Removing python file
    win_file:
      path: D:/update_browsers.py
      state: absent
    
  - name: Removing json file
    win_file:
      path: D:/output.json
      state: absent
    ignore_errors: true

" >> playbook.yml
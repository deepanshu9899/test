import sys
import requests
import json
import os
import zipfile
import re
import shutil

update_choice=sys.argv[1]
deletion_choice=sys.argv[2]
os_type=sys.argv[3]
print("update choice is: ",update_choice)
print("deletion choice is: ",deletion_choice)

if (os_type == "windows-10"):
    chrome_browser_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Google-Chrome.zip"
    chrome_browser_path="G:\\chrome"
    chrome_driver_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Google-Chrome-driver.zip"
    chrome_driver_path="G:\\drivers\\Chrome"
    edge_browser_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Edge.zip"
    edge_browser_path="G:\\edge" 
    edge_driver_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Edge-driver.zip"
    edge_driver_path= "G:\\drivers\\edge"
    firefox_browser_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Firefox.zip"
    firefox_browser_path="G:\\firefox"
    firefox_driver_download="C:\\Users\\ltuser.ghtestVM\\Downloads\\Firefox-driver.zip"
    firefox_driver_path="G:\\drivers\\Gecko"
    directories_path=["G:\\chrome", "G:\\drivers\Chrome", "G:\\firefox", "G:\\edge", "G:\\drivers\\edge"]
elif (os_type == "windows-11"):
    chrome_browser_download="C:\\Users\\ltuser\\Downloads\\Google-Chrome.zip"
    chrome_browser_path="G:\\chrome"
    chrome_driver_download="C:\\Users\\ltuser\\Downloads\\Google-Chrome-driver.zip"
    chrome_driver_path="G:\\drivers\\Chrome"
    edge_browser_download="C:\\Users\\ltuser\\Downloads\\Edge.zip"
    edge_browser_path="G:\\edge" 
    edge_driver_download="C:\\Users\\ltuser\\Downloads\\Edge-driver.zip"
    edge_driver_path= "G:\\drivers\\edge"
    firefox_browser_download="C:\\Users\\ltuser\\Downloads\\Firefox.zip"
    firefox_browser_path="G:\\firefox"
    firefox_driver_download="C:\\Users\\ltuser\\Downloads\\Firefox-driver.zip"
    firefox_driver_path="G:\\drivers\\Gecko"
    directories_path=["G:\\chrome", "G:\\drivers\Chrome", "G:\\firefox", "G:\\edge", "G:\\drivers\\edge"]
else:
    print("Wrong entry")

def download_browser_driver(url,output_file,path):
    response = requests.get(url)
    with open(output_file, 'wb') as zip_file:
        zip_file.write(response.content)
    with zipfile.ZipFile(output_file, 'r') as zip_ref:
        zip_ref.extractall(path)
    zip_ref.close()
    os.remove(output_file)

def download_json_from_url(url, output_file):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        with open(output_file, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
        print(f"JSON data downloaded successfully and saved to {output_file}")
    else:
        print(f"Failed to download JSON data. Status code: {response.status_code}")

def check_and_match_contents(chrome_highest_version,edge_highest_version,firefox_highest_version):
    pattern = r'\b\d+\.\d+\b'
    chrome_top_versions=[chrome_highest_version - i for i in range(10)]
    edge_top_versions=[edge_highest_version - i for i in range(10)]
    firefox_top_versions=[firefox_highest_version - i for i in range(10)]
    for directory in directories_path:
        contents = os.listdir(directory)

        print("contents of: ",directory," are: \n",contents)
        if (directory == "G:\\chrome"):
            chrome_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
            chrome_install_versions=[]
            print("present chrome versions: ",chrome_ver_present)
            for x in chrome_top_versions:
                if x in chrome_ver_present:
                    pass
                else:
                    chrome_install_versions.append(x)
        elif (directory == "G:\\firefox"):
            firefox_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
            firefox_install_versions=[]
            print("firefox ver present: ",firefox_ver_present)
            for x in firefox_top_versions:
                if x in firefox_ver_present:
                    pass
                else:
                    firefox_install_versions.append(x)
        elif (directory == "G:\\edge"):
            edge_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
            edge_install_versions=[]
            print("edge ver present: ",edge_ver_present)
            for x in edge_top_versions:
                if x in edge_ver_present:
                    pass
                else:
                    edge_install_versions.append(x)
        else:
            pass
    return(chrome_install_versions,edge_install_versions,firefox_install_versions)

def validate_installation(directory_path, browser_installed_versions):
    print("verifying installations")
    if ("G:\\chrome" in directory_path):
        for bvers in browser_installed_versions:
            validate_path=directory_path+"\\Google Chrome "+str(bvers)
            if os.path.exists(validate_path) and os.path.isdir(validate_path):
                print("directory: ",directory_path,"Google Chrome ",bvers," exists.")
            else:
                print("error in finding: ",directory_path,"Google Chrome ",bvers,"\n Please check installation.")
    elif ("G:\\edge" in directory_path):
        for bvers in browser_installed_versions:
            validate_path=directory_path+"\\Edge "+str(bvers)
            if os.path.exists(validate_path) and os.path.isdir(validate_path):
                print("directory: ",directory_path,"Edge ",bvers," exists.")
            else:
                print("error in finding: ",directory_path,"Edge ",bvers,"\n Please check installation.")
    elif ("G:\\firefox" in directory_path):
        for bvers in browser_installed_versions:
            validate_path=directory_path+"\\"+str(bvers)
            if os.path.exists(validate_path) and os.path.isdir(validate_path):
                print("directory: ",directory_path,bvers," exists.")
            else:
                print("error in finding: ",directory_path,bvers,"\n Please check installation.")
    else:
        print("error in validate_install")


def delete_contents(directory):
    pattern = r'\b\d+\.\d+\b'
    if ("chrome" in directory or "Chrome" in directory):
        contents = os.listdir(directory)
        print("contents of: ",directory," are: \n",contents)
        chrome_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
        sorted_versions = sorted(map(float, chrome_ver_present))
        print("Sorted versions in ascending order:", sorted_versions)
        chrome_delete_versions=sorted_versions[:-10]
        print("In directory: ",directory," delete versions: ",chrome_delete_versions)
        if ("drivers" in directory):
            for dc in chrome_delete_versions:
                ver_path=str(dc)
                del_path=os.path.join(directory,ver_path)
                print(del_path)
                shutil.rmtree(del_path)
        else:
            for dc in chrome_delete_versions:
                ver_path="Google Chrome "+str(dc)
                del_path=os.path.join(directory,ver_path)
                print(del_path)
                shutil.rmtree(del_path)
    elif ("firefox" in directory):
        contents = os.listdir(directory)
        firefox_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
        sorted_versions = sorted(map(float, firefox_ver_present))
        print("Sorted versions in ascending order:", sorted_versions)
        firefox_delete_versions=sorted_versions[:-10]
        print("In directory: ",directory," delete versions: ",firefox_delete_versions)
        for fc in firefox_delete_versions:
            ver_path=str(fc)
            del_path=os.path.join(directory,ver_path)
            print(del_path)
            shutil.rmtree(del_path)   
    elif ("edge" in directory):
        contents = os.listdir(directory)
        edge_ver_present = [float(re.search(pattern, string).group()) for string in [str(file_name) for file_name in contents] if re.search(pattern, string)]
        sorted_versions = sorted(map(float, edge_ver_present))
        print("Sorted versions in ascending order:", sorted_versions)
        edge_delete_versions=sorted_versions[:-10]
        print("In directory: ",directory," delete versions: ",edge_delete_versions)
        if ("drivers" in directory):
            for ec in edge_delete_versions:
                ver_path=str(ec)
                del_path=os.path.join(directory,ver_path)
                print(del_path)
                shutil.rmtree(del_path)
        else:
            for ec in edge_delete_versions:
                ver_path="Edge "+str(ec)
                del_path=os.path.join(directory,ver_path)
                print(del_path)
                shutil.rmtree(del_path)
    else:
        print("Deletion error")



if (update_choice=="latest"):
    url = "https://api.hyperexecute.cloud/v2.0/browsers"  
    output_file = "D:\\output.json"  
    download_json_from_url(url, output_file)
    with open('D:\\output.json', 'r') as file:
        data = json.load(file)    
    if (data):
        print("Data is loaded")
    else:
        print("Data not loaded")

    if (os_type == "windows-10"): 
        chrome_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'Chrome' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 10'])
        edge_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'MicrosoftEdge' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 10'])
        firefox_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'Firefox' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 10'])
    elif (os_type == "windows-11"):
        chrome_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'Chrome' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 11'])
        edge_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'MicrosoftEdge' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 11'])
        firefox_highest_version = max([float(browser['version']) for platform in data.get('platforms', {}).get('desktop', []) for browser in platform.get('browsers', []) if browser.get('name') == 'Firefox' and browser.get('version', '').replace('.', '').isdigit() and platform.get('platform') == 'Windows 11'])
    else:
        print("wrong os select")      
    print("Highest version of Chrome:", chrome_highest_version)
    print("Highest version of Edge:", edge_highest_version)
    print("Highest version of Firefox:", firefox_highest_version)

    chrome_install_versions,edge_install_versions,firefox_install_versions=check_and_match_contents(chrome_highest_version,edge_highest_version,firefox_highest_version)
    print("installing these chrome versions: ",chrome_install_versions)
    print("edge install versions: ",edge_install_versions)
    print("firefox install versions: ",firefox_install_versions)
    print("Downloading chrome versions")
    for c in chrome_install_versions:
        chrome_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/chrome/Google+Chrome+"+str(c)+".zip"
        chrome_driver_version="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Chrome/"+str(c)+".zip"
        print("Chrome browser: ", chrome_browser_link)
        print("Chrome driver: ", chrome_driver_version)
        download_browser_driver(chrome_browser_link,chrome_browser_download,chrome_browser_path)
        download_browser_driver(chrome_driver_version,chrome_driver_download,chrome_driver_path)
        

    print("Downloading edge versions")
    for e in edge_install_versions:
        edge_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/Edge+"+str(e)+".zip"
        edge_driver_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Edge/"+str(e)+".zip"
        print("Edge browser: ",edge_browser_link)
        print("Edge driver: ", edge_driver_link)
        download_browser_driver(edge_browser_link,edge_browser_download,edge_browser_path)
        download_browser_driver(edge_driver_link,edge_driver_download,edge_driver_path)
        


    print("Downloading firefox versions")
    for f in firefox_install_versions:
        firefox_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/firefox/"+str(f)+".zip"
        print("Firefox browser: ", firefox_browser_link)
        download_browser_driver(firefox_browser_link,firefox_browser_download,firefox_browser_path)

    validate_installation(chrome_browser_path,chrome_install_versions)
    validate_installation(edge_browser_path,edge_install_versions)   
    validate_installation(firefox_browser_path,firefox_install_versions)

elif ("-" in update_choice):
    print("downloading custom versions")
    custom_version=sys.argv[1].split(",")
    for choice in custom_version:
        browser_name=choice.split("-")[0]
        browser_version=choice.split("-")[1]
        driver_version=choice.split("-")[2]
        print("browser name: ",browser_name)
        print("browser version: ",browser_version)
        print("driver version: ",driver_version)

        if (browser_name == "chrome"):
            chrome_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/chrome/Google+Chrome+"+str(browser_version)+".0.zip"
            chrome_driver_version="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Chrome/"+str(driver_version)+".0.zip"
            print("Chrome browser: ", chrome_browser_link)
            print("Chrome driver: ", chrome_driver_version)
            download_browser_driver(chrome_browser_link,chrome_browser_download,chrome_browser_path)
            download_browser_driver(chrome_driver_version,chrome_driver_download,chrome_driver_path)

        elif (browser_name == "edge"):
            edge_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/edge/Edge+"+str(browser_version)+".0.zip"
            edge_driver_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Edge/"+str(driver_version)+".0.zip"
            print("Edge browser: ",edge_browser_link)
            print("Edge driver: ", edge_driver_link)
            download_browser_driver(edge_browser_link,edge_browser_download,edge_browser_path)
            download_browser_driver(edge_driver_link,edge_driver_download,edge_driver_path)

        elif (browser_name == "firefox"):
            firefox_browser_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/firefox/"+str(browser_version)+".0.zip"
            firefox_driver_link="https://stage-ltbrowserdeploy.lambdatestinternal.com/windows/drivers/Gecko/"+str(driver_version)+".0.zip"
            print("Firefox browser: ", firefox_browser_link)
            download_browser_driver(firefox_browser_link,firefox_browser_download,firefox_browser_path)
            download_browser_driver(firefox_driver_link,firefox_driver_download,firefox_driver_path)
        else:
            print("Wrong browser name")
elif (update_choice == "no-install"):
    pass
else:
    print("Wrong entry. \n 1. latest \n 2. browserName-browserVersion-driverVersion \n 3. no-install")


if(deletion_choice == "True"):
    for directory in directories_path:
        print("Keeping only the top 10 browser in directory: ",directory," Deleting the rest")
        delete_contents(directory)

elif(deletion_choice == "False"):
    print("not deleting any browsers or drivers")
else:
    print("Wrong deletion choice")




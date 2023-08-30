import re
from datetime import datetime, timedelta
import requests
import subprocess
import requests
import ssl
import speedtest
import smtplib
import socket
import time
import ssl
import subprocess
import os
import shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess


# Restart the computer **
def restart_computer():
    try:
        subprocess.run(["shutdown", "/r", "/t", "0"], check=True)
    except subprocess.CalledProcessError as e:
        print("Error during restarting server:", e)


# Send email **
def send_email(subjectMail, messageMail, senderMail, emailTo, serverSmtp, portSmtp, usernameSmtp, passwordSmtp):
    msg = MIMEMultipart()
    msg['From'] = senderMail
    msg['To'] = emailTo
    msg['subjectMail'] = subjectMail

    body = MIMEText(messageMail, 'plain')

    msg.attach(body)

    try:
        server = smtplib.SMTP(serverSmtp, portSmtp)
        server.starttls()
        server.login(usernameSmtp, passwordSmtp)
        server.sendmail(senderMail, emailTo, msg.as_string())
        server.quit()
        print("Email is send to sender!")
    except Exception as e:
        print("Email failed to send:", str(e))


# Clean Logs - move and delete **
def get_drive_usage(driveLocation):
    total, used, free = shutil.disk_usage(driveLocation)
    return used / total * 100


# move logs from source to destination
def move_old_logs(sourceLocation, destinationLocation, months):
    currentTime = datetime.now()
    cutoffDate = currentTime - timedelta(days=months * 30)

    for root, dirs, files in os.walk(sourceLocation):
        for file in files:
            filePath = os.path.join(root, file)
            fileMtime = datetime.fromtimestamp(os.path.getmtime(filePath))

            if fileMtime < cutoffDate:
                shutil.move(filePath, os.path.join(destinationLocation, file))


def clean_logs():
    driveCpath = "C:"  # Update this with the actual path for drive C
    driveDpath = "D:"  # Update this with the actual path for drive D
    netLogsPath = os.path.join(driveCpath, "path_to_net_logs")  # Update with the actual path to .NET logs

    if get_drive_usage(driveCpath) >= 90:
        move_old_logs(netLogsPath, driveDpath, 3)

    move_old_logs(netLogsPath, driveDpath, 3)


# Update app List_library **
def find_list_library_update(logsErrors):
    ListLibraryToUpdate = set()

    libraryPattern = re.compile(r'(?<=requires )\'([\w.-]+)')

    for errorLog in logsErrors:
        match = libraryPattern.search(errorLog)
        if match:
            ListLibraryToUpdate.add(match.group(1))

    return ListLibraryToUpdate


# install libraries
def update_list_library(List_library):
    for library in List_library:
        subprocess.run(['pip', 'install', '--upgrade', library])
        print(f"Updated {library} to the latest version.")



# IIS Monitoring, ssl, check api running, web download speed**
def check_valid_ssl(url_string):
    try:
        response = requests.get(url_string)
        if response.status_code == 200:
            cert = ssl.get_server_certificate((url_string, 443))
            x509 = ssl.PEM_cert_to_DER_cert(cert)
            return True
    except requests.ConnectionError:
        return False
    return False


# check if the api is running and can be accessed on the web
def check_api_running(urlStringApi):
    try:
        response = requests.get(urlStringApi)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False
    return False


# check if users can access the web app
def check_web_app_access(url_string):
    try:
        response = requests.get(url_string)
        if response.status_code == 200:
            return True
    except requests.ConnectionError:
        return False
    return False


# check internert speed
def check_download_speed():
    url_string = "http://speedtest.ftp.otenet.gr/files/test100Mb.db"
    startTime = time.time()
    response = requests.get(url_string)
    endTime = time.time()

    if response.status_code == 200:
        downloadTime = endTime - startTime
        downloadSpeed = (100 * 8) / (downloadTime * 1024 * 1024)
        return downloadSpeed
    else:
        return None


# SQL Server - database **
def is_sql_server_running():
    try:
        result = subprocess.run(["sc", "query", "MSSQLSERVER"], capture_output=True, text=True, check=True)
        return "RUNNING" in result.stdout
    except subprocess.CalledProcessError:
        return False


# start the sql server
def start_sql_server():
    try:
        subprocess.run(["net", "start", "MSSQLSERVER"], check=True)
        print("SQL SERVER IS RUNNING.")
    except subprocess.CalledProcessError as e:
        print(f"Error from SQL Server occured: {e}")


# restart the sql server
def restart_sql_server():
    try:
        subprocess.run(["net", "stop", "MSSQLSERVER"], check=True)
        time.sleep(5)  # Wait for a few seconds before starting again
        subprocess.run(["net", "start", "MSSQLSERVER"], check=True)
        print("SQL Server has restarted.")
    except subprocess.CalledProcessError as e:
        print(f"Error occured during restarting of SQL Server: {e}")


# check if the sql server is running on the os
def check_and_manage_sql_server():
    if not is_sql_server_running():
        start_sql_server()
    else:
        print("SQL Server is already running.")

    # Simulate checking for database errors
    databaseHasErrors = False  # Replace with actual check
    if databaseHasErrors:
        restart_sql_server()
    else:
        print("Database does not have errors")


# main operations **
def main():
    # Fill in your email and server details here
    subjectMail = "***************"
    messageMail = "***************"
    senderMail = "***************"
    emailTo = "***************"
    serverSmtp = "***************"
    portSmtp = 587
    usernameSmtp = "***************"
    passwordSmtp = "***************"
    # url_strings
    url_string_iis = "***************"
    urlStringApi = "***************"
    urlStringWebApp = "***************"
    # send email
    send_email(subjectMail, messageMail, senderMail, emailTo, serverSmtp, portSmtp, usernameSmtp, passwordSmtp)
    # Storage **
    try:
        with open('loadFile.txt', 'r') as file:
            logsErrors = file.readlines()
    except FileNotFoundError:
        print("Error log file not found.")
        return

    ListLibraryToUpdate = find_list_library_update(logsErrors)

    if ListLibraryToUpdate:
        print("List_library that need to be updated:")
        for library in ListLibraryToUpdate:
            print(library)

        update_list_library(ListLibraryToUpdate)
    else:
        print("No List_library need to be updated.")
    # IIS **
    iis_ssl_valid = check_valid_ssl(url_string_iis)
    api_running = check_api_running(urlStringApi)
    web_app_accessible = check_web_app_access(urlStringWebApp)
    downloadSpeed = check_download_speed()

    print("IIS SSL Valid:", iis_ssl_valid)

    print("API Running:", api_running)

    print("Web App Accessible:", web_app_accessible)

    if downloadSpeed is not None:
        print(f"Internet Speed Is: {downloadSpeed:.2f} Mbps")
    else:
        print("Internet Speed Testing Failed")


# SQL Server **
check_and_manage_sql_server()

# Clean Logs **
clean_logs()
#  restart computer **
# restart_computer()
if __name__ == "__main__":
    main()

#!/usr/bin/env python3

# MIT License
#
# Copyright (c) 2018 Cosmos Coin Developers, https://cosmoscoin.co/
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import time

import json
import paramiko

from io import BytesIO
from urllib.request import urlopen

DEFAULT_DECODE = "utf-8"

CHECK_RELEASE_COMMAND = "lsb_release -a"
UPDATE_TOOLS_COMMAND = "apt-get -y update && apt-get -y upgrade && apt-get -y install wget"

INSTALL_COIN_COMMAND = "mkdir -p /home/{0} && " \
                        "wget -qO- {1} | tar xvz --strip-components=1 -C /home/{0} && " \
                        "cp /home/{0}/bin/* /usr/local/bin"

GET_LATEST_GIT_RELEASE_COMMAND = "https://api.github.com/repos/{0}/{1}/releases/latest"
                        
IS_COIN_INSTALLED_COMMAND = "command -v {0}"
CHECK_IF_PROCESS_RUNNING_COMMAND_FMT = "ps cax | grep {0} > /dev/null"

def openChannel(server, username, password):
    """Open an SSH channel with the specified server.
    
    Args:
        server (str): The IP address of the server to connect to.
        username (str): The username to be used in the connection.
        password (str): The password associated with the user.
    
    Returns:
        Obj: A client object containing the state of the connection.
    """
    channel = paramiko.SSHClient()
    channel.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    channel.connect(server, username=username, password=password)
    
    return channel
    
def closeChannel(channel):
    """Close a previously open SSH connection.
    
    Args:
        channel (obj): The client object returned by the open function.
    """
    channel.close()
    
def sendCommand(channel, command):
    """Send a comment across the channel and return the results.
    
    Args:
        channel (obj): The client object returned by the open function.
        command (str): The command to be executed.
    Returns:
        Str: A string object containing the command results.
    """        
    output = BytesIO()
    stdin, stdout, stderr = channel.exec_command(command)
    
    # Parse the partial command output while the command is running
    while not stdout.channel.exit_status_ready():
        while stdout.channel.recv_ready():
            output.write(stdout.channel.recv(1024))
        
        time.sleep(2)
    
    # Parse any remaining channel output
    while stdout.channel.recv_ready():
        output.write(stdout.channel.recv(1024))
        
    # Parse any error channel output
    while stderr.channel.recv_ready():
        output.write(stderr.channel.recv(1024))

    exitStatus = stdout.channel.recv_exit_status()
    
    if exitStatus != 0:
        raise ValueError("Command: \"{0}\" failed with status: {1}".format(command, exitStatus))
        
    return output.getvalue().decode(DEFAULT_DECODE)

def createFileWithContents(server, username, password, filePath, data):
    """Create a file on the specified server with the contents provided.
    
    Args:
        server (str): The IP address of the server to connect to.
        username (str): The username to be used in the connection.
        password (str): The password associated with the user.
        filePath (str): The relative path of the file to be written (relative to $HOME)
        data (str): The data to be written into the file.
    """        
    directory = os.path.dirname(filePath)
    
    # Open SSH connection
    channel = openChannel(server, username, password)
    sftp = channel.open_sftp()

    # Create directory if necessary
    try:
        sftp.mkdir(directory)
    except IOError:
        pass
      
    # Transfer and replace the file contents
    try:
        with sftp.open(filePath, 'w') as f:
            f.write(data)
    finally:
        # Close ssh connection
        closeChannel(channel)
        
def checkRelease(channel, codeName):
    """Check and verify the release on the VPS server.

    Args:
        channel (obj): The client object returned by the open function.
        codeName (str): The expected release code name to verify.
    """    
    print("Checking VPS operating system release..\n")
    output = sendCommand(channel, CHECK_RELEASE_COMMAND)
    
    print(output)
    if codeName not in output:
        raise ValueError("Unsupported operating system, refer to documentation for more info")

def checkDaemonNotRunning(channel, daemonName):
    """Check that the daemon is not currently running. This is done to avoid potential problems in the future.

    Args:
        channel (obj): The client object returned by the open function.
        daemonName (str): The name of the daemon to check.
    """
    print("Checking that daemon is not currently running on VPS..")
    if isProcessRunning(channel, daemonName):
        message = "The \'{0}\' daemon is currently running, please stop it and try again".format(daemonName)
        raise ValueError(message)
        
    print("")
        
def updateTools(channel):
    """Update the installation and tools on the VPS.
    
    Note: The output won't be printed until the update is complete.

    Args:
        channel (obj): The client object returned by the open function.
    """    
    print("Updating tools on VPS..\n")
    print(sendCommand(channel, UPDATE_TOOLS_COMMAND))

def getInstallCommand(coinName, gitOwner, gitProject, namePattern):
    """Determine the installation command based on the coin's latest release.
    
    Args:
        coinName (str): Name of the coin to install.
        gitOwner (str): The Git owner of the project.
        gitProject (str): The name of the project in Git.
        namePattern (str): A pattern to be used to identify the release version to get.
        
    Returns:
        String: A string containing the install command to be executed.
    """
    print("Get the latest masternode release")
    
    url = GET_LATEST_GIT_RELEASE_COMMAND.format(gitOwner, gitProject)
    releases = json.load(urlopen(url))

    matches = [release for release in releases["assets"] if namePattern in release["name"]]
        
    if len(matches) != 1:
        message = "Unexpected number of matches: {0} for the specified pattern {1}, please check configuration".format(len(txValues), namePattern)
        raise ValueError(message)
        
    downloadUrl = matches[0]["browser_download_url"]    
    print("Latest release found: {0}\n".format(downloadUrl))
    return INSTALL_COIN_COMMAND.format(coinName, downloadUrl)
    
def installMasternode(coinName, channel, daemonName, installCommand):
    """Install the masternode binaries on the VPS.

    Args:
        channel (obj): The client object returned by the open function.
        daemonName (str): The name of the daemon binary associated with the installation.
        installCommand (str): The full command to be executed for installation.
    """
    print("Installing masternode on VPS..")
    print("Install command:\n\n{0}\n".format(installCommand))
    
    try:
        # This command will fail if masternode binaries already installed
        sendCommand(channel, IS_COIN_INSTALLED_COMMAND.format(daemonName))
    except:
        print(sendCommand(channel, installCommand))
    else:
        print("{0} is already installed.. skipping installation.\n".format(coinName))    

def isProcessRunning(channel, processName):
    """Check if the specified process is currently running.
    
    Args:
        channel (obj): The client object returned by the open function.
        processName (str): The name of the process to check.
    
    Returns:
        Boolean: True if the process is running, False otherwise.
    """
    try: 
        # If process is not running, an exception is raised
        command = CHECK_IF_PROCESS_RUNNING_COMMAND_FMT.format(processName)
        sendCommand(channel, command)
    except:
        return False
    else:
        return True

def createUser(channel, coinName):
    """Creates a user for the coin if necessary.
    
    Args:
        channel (obj): The client object returned by the open function.
        coinName (str): Name of the coin.
    """
    print("Creating user for masternode: {0}, if necessary..".format(coinName))
    
    try:
        # If this command fails, the user doesn't exist
        sendCommand(channel, "id -u {0}".format(coinName))
    except:
        # Create user
        sendCommand(channel, "useradd {0}".format(coinName))
 
    print("")
 
def sendSingleCommand(server, user, password, command):
    """Wrapper function to open a connection and execute a single command.
    
    Args:
        server (str): The IP address of the server to connect to.
        username (str): The username to be used in the connection.
        password (str): The password associated with the user.
        command (str): The command to be executed.
        
    Returns:
        String: String containing the command output.
    """
    # Open SSH connection
    channel = openChannel(server, user, password)
    
    output = ""
    try:
        output = sendCommand(channel, command)
    finally:
        # Close ssh connection
        closeChannel(channel)

    return output
        
def setup(server, user, password, config):
    """Program entry point. This function will setup the VPS per the coin requirements.

    Args:
        server (str): The IP address of the server to connect to.
        username (str): The username to be used in the connection.
        password (str): The password associated with the user.
        config (dict): Dictionary containing the options parsed by the utility.
    """
    # Open SSH connection
    channel = openChannel(server, user, password)
    
    try:
        # Check that OS is the right version
        checkRelease(channel, config["VPS"]["UbuntuCodename"])
        
        # Check that daemon is not running
        checkDaemonNotRunning(channel, config["Coin"]["Daemon"])
    
        # Update OS tools
        updateTools(channel)
    
        # Install masternode
        installCommand = getInstallCommand(config["Coin"]["Name"], config["Git"]["Owner"], config["Git"]["Project"], config["Git"]["NamePattern"])
        installMasternode(config["Coin"]["Name"], channel, config["Coin"]["Daemon"], installCommand)
        
        # Create user for masternode
        createUser(channel, config["Coin"]["Name"])
    finally:
        # Close ssh connection
        closeChannel(channel)

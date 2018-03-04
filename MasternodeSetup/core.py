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
import glob
import time
import json

import pprint
import string
import random

import getpass
import subprocess

from . import vps
from . import daemon

from os import environ

RPC_USER_LENGTH = 32
RPC_PASSWORD_LENGTH = 32

CONF_TEMPLATE_FILE = os.path.join(os.path.dirname(__file__), "conf", "conf.template")
ACTIVATION_STRING = "waiting for remote activation"

def checkIfEnvironmentDefined(envHome, envUser):
    """Checks if the required environment variables are defined.
    
    Args:
        envHome (str): The name of the home environment variable.
        envUser (str): The name of the user environment variable.
    """
    if envHome not in environ:
        raise ValueError("Please set {0} environment variable".format(envHome))
        
    elif envUser not in environ:
        raise ValueError("Please set {0} environment variable".format(envUser))
       
def checkIfWalletInstalled(cli, daemonCli):
    """Check if the local wallet is installed.

    Args:
        cli (str): The full path of the local cli binary.
        daemonCli (str): The full path of the local daemon binary.
    """
    if not glob.glob("{0}*".format(cli)):
        raise ValueError("Unable to find file: {0}, please check your installation".format(cli))
    
    elif not glob.glob("{0}*".format(daemonCli)):
        raise ValueError("Unable to find file: {0}, please check your installation".format(daemonCli))

def setupWallet(walletConfFile):
    """This function will setup the local wallet requirements.
    
    Args:
        walletConfFile (str): Full path to wallet conf file.
    """
    print("Setup wallet configuration..")
    if "rpcuser" not in open(walletConfFile).read():
        print("Creating rpcuser setting..")
        with open(walletConfFile, "a") as f:
            f.write("rpcuser={0}\n".format(generateRandomString(RPC_USER_LENGTH)))
            
    if "rpcpassword" not in open(walletConfFile).read():
        print("Creating rpcpassword setting..")
        with open(walletConfFile, "a") as f:
            f.write("rpcpassword={0}\n".format(generateRandomString(RPC_PASSWORD_LENGTH)))
    
    print("")
    
def startLocalDaemon(daemonCli):
    """Start the local daemon. Required to use the coin cli.
    
    Args:
        daemonCli (str): The full path of the local daemon binary.
        
    Returns:
        Obj: The process associated with the daemon that was started.
    """    
    print("Starting local daemon..")
    
    try:
        proc = daemon.start(daemonCli)
        
        # Ensure that the daemon did not fail and is still running
        proc.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        pass
    else:
        raise ValueError("Failed to start local daemon")
        
    print("")
    return proc

def stopLocalDaemon(cli):
    """Stop the local daemon.
    
    Args:
        cli (str): The full path of the local cli binary.
    """    
    print("Stopping local daemon..")
    try:
        daemon.stop(cli)
    except:
        raise ValueError("Failed to stop local daemon")
        
    print("")

def pollForWalletSync(cli):
    """Poll for the wallet to be fully synced (on daemon).
    
    Utilizes the blockchain info RPC call to check that verification in progress
    is at least 1.00. This field is an estimate of the synchronization status. 
    Checking this number ensures we are in sync with a good confidence level.
    
    Args:
        cli (str): The full path of the local cli binary.
    """    
    print("Wait for wallet to by synchronized..")
    blockchaininfo = daemon.getBlockchainInfo(cli)
    blockchainvalues = json.loads(blockchaininfo)

    # Loop continuously until we know we are synced
    while blockchainvalues["verificationprogress"] < 1:
        blockchaininfo = daemon.getBlockchainInfo(cli)
        blockchainvalues = json.loads(blockchaininfo)

        print("Progress.. {0}%".format(blockchainvalues["verificationprogress"] * 100))
        time.sleep(5)
     
    print("")
            
def getTotalUnlockedBalance(cli):
    """Get the total balance in wallet without accounting for locked coins (i.e. from masternodes)
    
    Args:
        cli (str): The full path of the local cli binary.
        
    Returns:
        Int: The total unlocked balance present.
    """    
    output = daemon.listUnspent(cli)
    values = json.loads(output)
    
    return sum(input['amount'] for input in values)
    
def unlockWallet(cli):
    """Unlocks the wallet temporarily so that other operations may be performed.
    
    Args:
        cli (str): The full path of the local cli binary.
    """    
    done = False
    
    # Loop until the correct password is seen
    while done == False:
        try:
            passphrase = getpass.getpass(prompt="Please enter you wallet passphrase: ")
            output = daemon.unlockWallet(cli, passphrase)
        except:
            pass
            print("Incorrect passphrase, please try again..")
        else:
            done = True
    
    print("")
    
def sendCollateralToAddress(cli, address, collateral):
    """Send the collateral amount to the specified address.
    
    Args:
        cli (str): The full path of the local cli binary.
        address (str): The address to be used for the masternode.
        collateral (int): The collateral amount to be sent.
        
    Returns:
        String: The txid associated with this transaction.
    """    
    try:
        # If the wallet is not encrypted, no unlocking is necessary
        txid = daemon.sendToAddress(cli, address, collateral)
    
    except:
        print("Wallet is locked, please unlock your wallet..")
            
        unlockWallet(cli)
        txid = daemon.sendToAddress(cli, address, collateral)
    
    return txid

def getMasternodeOutput(cli, txid):
    """Get the masternode output containing the masternode txid.
    
    Args:
        cli (str): The full path of the local cli binary.
        txid (str): The txid associated with the collateral.
        
    Returns:
        Dict: A dictionary containing the masternode output
    """         
    output = daemon.getMasternodeOutputs(cli)
    values = json.loads(output)
    
    txValues = [value for value in values if value['txhash'] == txid]
    
    # There should be a single match, check to be sure
    if len(txValues) != 1:
        raise ValueError("Transaction: {0} was not found in masternode outputs".format(txid))
    
    return txValues[0]
    
def setupMasternodeTransaction(cli, label, collateral):
    """Performs a setup of the transactions required to create a masternode.
    
    Specifically:
    1. Check balance
    2. Generate address
    3. Send collateral to address
    4. Get masternode output
    5. Get masternode key
    
    Args:
        cli (str): The full path of the local cli binary.
        label (str): The label to be used when generating a new address.
        collateral (int): The collateral amount to be sent.
        
    Returns:
        2-Tuple: Tuple containing the masternode output and masternode key
    """         
    print("Setup masternode transaction..\n")
    
    # First check we have enough balance
    balance = getTotalUnlockedBalance(cli)
    print("Collateral required: {0}, total unlocked balance: {1}".format(collateral, balance))
    
    if balance < collateral:
        raise ValueError("Insufficient funds")    
    
    # Generate new address for masternode
    address = daemon.generateNewAddress(cli, label)
    print("Send collateral to new address: {{{0}: {1}}}".format(label, address))
    
    # Send collateral to new address
    txid = sendCollateralToAddress(cli, address, collateral)
    print("Sent collateral successfully, txid: {0}\n".format(txid))
    
    # Get masternode output associated with collateral
    print("Get masternode output..")
    masternodeOutput = getMasternodeOutput(cli, txid)
    print("Masternode output:\n{0}\n".format(masternodeOutput))
    
    # Get masternode key to be used
    print("Get masternode key..")
    masternodeKey = daemon.generateMasternodeKey(cli)
    print("Masternode key: {0}\n".format(masternodeKey))
    
    return (masternodeOutput, masternodeKey)

def generateRandomString(length):
    """Generate a random string of a specified length. To be used in rpc information.
    
    Args:
        length (int): Length of string to be generated.
        
    Returns:
        String: String that was generated.
    """
    choice = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(random.SystemRandom().choice(choice) for _ in range(length))

def setupVpsConfFile(server, user, password, confFile, masternodeKey):
    """Setup the vps masternode configuration file.
    
    Args:
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        confFile (str): The full path to the configuration file to be used.
        masternodeKey (str): The masternode key associated with this node.
    """
    print("Setup VPS conf file..")

    values = dict()
    
    # Generate random values for user and password
    values["rpcuser"] = generateRandomString(RPC_USER_LENGTH)
    values["rpcpassword"] = generateRandomString(RPC_PASSWORD_LENGTH)
    
    values["externalip"] = server
    values["masternodepivkey"] = masternodeKey  

    # Parse and replace template file with values
    source = ""
    with open(CONF_TEMPLATE_FILE) as template:
        source = string.Template(template.read())
    
    sourceFile = source.substitute(values)
    
    print("Generated configuration file:")
    pprint.pprint(sourceFile)
    print("")
    
    # Send configuration file to vps
    print("Send configuration file to VPS..")
    vps.createFileWithContents(server, user, password, confFile, sourceFile)
    print("Configuration file sent successfully!\n")

def updateVpsPermissions(server, user, password, coinName):
    """Updates the folder permissions for the coin user so that the daemon may run.
    
    Args:
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        coinName (str): The name of the coin.
    """
    print("Updating folder permissions for {0} user.".format(coinName))
    
    command = "chmod -R 777 /home/{0}".format(coinName)
    vps.sendSingleCommand(server, user, password, command)
    
    print("")
    
def stopVpsDaemon(cli, daemonCli, server, user, password, coinName): 
    """Stops the vps daemon if it's running.
    
    Args:
        cli (str): The name of the coin cli to be used.
        daemonCli (str): The name of the coin daemon to be used.
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        coinName (str): The name of the coin.
    """  
    print("Stopping daemon on VPS (if running)..")
    
    # Open SSH connection
    channel = vps.openChannel(server, user, password)    

    try: 
        if vps.isProcessRunning(channel, daemonCli):
            # Stop the process if it's currently running
            command = "su -c \"{0} stop\" {1}".format(cli, coinName)
            output = vps.sendCommand(channel, command)

            # Allow enough time for process to terminate
            time.sleep(20)
    finally:
        # Close ssh connection
        vps.closeChannel(channel)

    print("")
    
def startVpsDaemon(daemonCli, server, user, password, coinName):
    """Starts the vps daemon.
    
    Args:
        daemonCli (str): The name of the coin daemon to be used.
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        coinName (str): The name of the coin.
    """  
    print("Starting daemon on VPS..")
    
    # Open SSH connection
    channel = vps.openChannel(server, user, password)

    try:
        command = "su -c \"{0} -daemon\" {1}".format(daemonCli, coinName)
        print(vps.sendCommand(channel, command))
        
        # Allow enough time for daemon to start
        time.sleep(20) 

        if not vps.isProcessRunning(channel, daemonCli):
            raise ValueError("Failed to start daemon on VPS")
        
    finally:
        # Close ssh connection
        vps.closeChannel(channel)

def clearVpsDebugFile(server, user, password, debugFile):
    """Removes the debug file specified.

    Args:
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        debugFile (str): The name of the file to be removed.
    """
    print("Removing VPS debug file: {0}".format(debugFile))
    
    command = "rm -rf {0}".format(debugFile)
    vps.sendSingleCommand(server, user, password, command)
    
    print("")
    
def pollForVpsDaemonActivationReady(server, user, password, debugFile):
    """Waits until the daemon is ready to be activated.

    Args:
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        debugFile (str): The name of the file to search.
    """
    done = False
    command = "grep \"{0}\" {1} > /dev/null".format(ACTIVATION_STRING, debugFile)
        
    while done == False:
        try:
            print("Wait until VPS daemon is activation ready.. This may take some time..")
            vps.sendSingleCommand(server, user, password, command)
        except:
            time.sleep(10)
        else:
            done = True
    
    print("")
    
def setupVpsMasternode(cli, daemonCli, server, user, password, confFile, masternodeKey, coinName, debugFile):
    """Sets up the masternode on the VPS.  Specifically:
    
    1. Stop daemon (if necessary).
    2. Copy masternode conf file to vps.
    3. Start daemon.
    
    Args:
        cli (str): The name of the coin cli to be used.
        daemonCli (str): The name of the coin daemon to be used.
        server (str): The IP address of the server to connect to.
        user (str): The username to be used in the connection.
        password (str): The password associated with the user.
        confFile (str): The full path to the configuration file to be used.
        masternodeKey (str): The masternode key associated with this node. 
        coinName (str): The name of the coin.
    """  
    # We must stop the current daemon to prevent issues with the conf file
    stopVpsDaemon(cli, daemonCli, server, user, password, coinName)
        
    # Load new conf file
    setupVpsConfFile(server, user, password, confFile, masternodeKey)
    
    # We must update folder permissions so that daemon can run
    updateVpsPermissions(server, user, password, coinName)
    
    # Clear debug file so that it can be searched later
    clearVpsDebugFile(server, user, password, debugFile)
    
    # Start daemon
    startVpsDaemon(daemonCli, server, user, password, coinName)
    
    # Poll for daemon to be ready for activation
    # Note: It seems like the activation doesn't work outside of wallet so disabling for now..
    #pollForVpsDaemonActivationReady(server, user, password, debugFile)

def setupMasternodeConfFile(server, label, masternodeConfFile, masternodePort, masternodeOutput, masternodeKey):
    """Sets up the local masternode conf file with the masternode values.
        
    Args:
        server (str): The IP address of the server to connect to.
        label (str): The label to be used when generating a new address.
        masternodeConfFile (str): The full path to the masternode conf file.
        masternodePort (int): The port number associated with the masternode.
        masternodeOutput (dict): The masternode output containing the collateral txinfo.
        masternodeKey (str): The masternode key associated with this node.        
    """  
    print("Setup masternode conf file..")
    
    # Append to the existing file
    with open(masternodeConfFile, 'a') as f:
        line = "\n{0} {1}:{2} {3} {4} {5}".format(label, server, masternodePort, masternodeKey, masternodeOutput["txhash"], masternodeOutput["outputidx"])
        f.write(line)

def startMasternodeAlias(cli, label):
    """Start the masternode by its alias.
    
    Args:
        cli (str): The name of the coin cli to be used.
        label (str): The label to be used when generating a new address.
    """
    print("Start masternode..")
    
    try:
        # If the wallet is not encrypted, no unlocking is necessary
        daemon.masternodeStartAlias(cli, label)
    
    except:
        print("Wallet is locked, please unlock your wallet..")
            
        unlockWallet(cli)
        daemon.masternodeStartAlias(cli, label)    

    print("Masternode started successfully!")

def setupWalletForMasternode(cli, server, label, masternodeConfFile, masternodePort, masternodeOutput, masternodeKey):
    """Sets up the wallet for the newly created masternode.
        
    Args:
        cli (str): The name of the coin cli to be used.    
        server (str): The IP address of the server to connect to.
        label (str): The label to be used when generating a new address.
        masternodeConfFile (str): The full path to the masternode conf file.
        masternodePort (int): The port number associated with the masternode.        
        masternodeOutput (dict): The masternode output containing the collateral txinfo.
        masternodeKey (str): The masternode key associated with this node.        
    """  
    setupMasternodeConfFile(server, label, masternodeConfFile, masternodePort, masternodeOutput, masternodeKey)
    startMasternodeAlias(cli, label)

def getCoinBinaries(envHome, cliName, daemonName):
    """Gets the full paths of the binaries associated with this coin.
    
    Args:
        envHome (str): The name of the home environment variable.
        cliName (str): The name of the cli binary associated with this coin.
        daemonName (str): The name of the daemon binary associated with this coin.
        
    Returns:
        2-Tuple: Tuple containing the full paths as described.
    """
    homePath = environ.get(envHome)

    cli = os.path.join(homePath, "daemon", cliName)
    daemonCli = os.path.join(homePath, "daemon", daemonName)
    
    return (cli, daemonCli)

def getCoinFiles(envUser, walletConf, masternodeConf):    
    """Gets the full paths of the conf files associated with this coin.
    
    Args:
        envUser (str): The name of the user environment variable.
        walletConf (str): The name of the wallet conf file.
        masternodeConf (str): The name of the masternode conf file.
        
    Returns:
        2-Tuple: Tuple full paths as described.
    """
    userPath = environ.get(envUser)
    
    walletConfFile = os.path.join(userPath, walletConf)
    masternodeConfFile = os.path.join(userPath, masternodeConf)
    
    return (walletConfFile, masternodeConfFile)

def checkPrerequisites(config):
    """Checks that certain prerequisits are met before continuing. Specifically:
    
    1. Check that necessary environment variables are defined.
    2. Check that the local wallet is installed.
    
    Args:
        envUser (str): The name of the user environment variable.
        masternodeConf (str): The name of the masternode conf file.
    """
    print("Checking wallet requirements..")    
    
    cli, daemonCli = getCoinBinaries(config["Environment"]["Home"], config["Coin"]["Cli"], config["Coin"]["Daemon"])    
    checkIfEnvironmentDefined(config["Environment"]["Home"], config["Environment"]["User"])
    checkIfWalletInstalled(cli, daemonCli)    
    
    print("")
        
def setup(server, user, password, label, config):
    """Top level function associated with this module. Responsible for the core configuration
    of this masternode. Specifically it will:
    
    1. Start local daemon.
    2. Poll for wallet to be synced.
    3. Perform masternode transactions.
    4. Setup masternode config on vps.
    5. Setup the local wallet for the masternode.
    6. Stop local daemon.
    """
    # Determine binary and file names based on config
    cli, daemonCli = getCoinBinaries(config["Environment"]["Home"], config["Coin"]["Cli"], config["Coin"]["Daemon"])
    walletConfFile, masternodeConfFile = getCoinFiles(config["Environment"]["User"], config["Wallet"]["WalletConf"], config["Wallet"]["MasternodeConf"])

    setupWallet(walletConfFile)
    localDaemon = startLocalDaemon(daemonCli)   
    
    try:
        pollForWalletSync(cli)
        masternodeOutput, masternodeKey = setupMasternodeTransaction(cli, label, float(config["Coin"]["Collateral"]))
        
        vpsConfFile = "/home/{0}/{1}/{2}".format(config["Coin"]["Name"], config["VPS"]["DataDir"], config["VPS"]["ConfFile"])
        vpsDebugFile = "/home/{0}/{1}/{2}".format(config["Coin"]["Name"], config["VPS"]["DataDir"], config["VPS"]["DebugFile"])
        
        setupVpsMasternode(config["Coin"]["Cli"], config["Coin"]["Daemon"], server, user, password, vpsConfFile, masternodeKey, config["Coin"]["Name"], vpsDebugFile)
        
        setupWalletForMasternode(cli, server, label, masternodeConfFile, int(config["Coin"]["Port"]), masternodeOutput, masternodeKey)

    finally:
        stopLocalDaemon(cli)
        localDaemon.wait()
    
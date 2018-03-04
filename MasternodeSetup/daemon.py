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

import subprocess

DEFAULT_DECODE = "utf-8"
WALLET_LOCK_TIMEOUT_SEC = 60

DAEMON_STOP_COMMAND = "{0} stop"
DAEMON_START_COMMAND = "{0} -daemon"

CLI_GET_BALANCE = "{0} getbalance"
CLI_LIST_UNSPENT = "{0} listunspent"

CLI_GET_BLOCKCHAIN_INFO = "{0} getblockchaininfo"
CLI_UNLOCK_WALLET = "{0} walletpassphrase {1} {2}"

CLI_SEND_TO_ADDRESS = "{0} sendtoaddress {1} {2}"
CLI_GENERATE_NEW_ADDRESS = "{0} getnewaddress {1}"

CLI_MASTERNODE_GENKEY = "{0} masternode genkey"
CLI_MASTERNODE_OUTPUTS = "{0} masternode outputs"
  
CLI_MASTERNODE_START_ALIAS = "{0} masternode start-alias {1}"  

def start(daemon):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        daemon (str): Full path to daemon binary associated with coin.
        
    Returns:
        String: String containing the command output.
    """
    command = DAEMON_START_COMMAND.format(daemon).split(" ")
    return subprocess.Popen(command, stdout=subprocess.PIPE)
    
def stop(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = DAEMON_STOP_COMMAND.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE)

def getBlockchainInfo(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_GET_BLOCKCHAIN_INFO.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE)
    
def generateNewAddress(cli, label):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        label (str): Label associated with the address to be generated.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_GENERATE_NEW_ADDRESS.format(cli, label)
    return subprocess.check_output(command).decode(DEFAULT_DECODE).strip()
    
def unlockWallet(cli, passphrase):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        passphrase (str): Passphrase to be used in wallet unlock.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_UNLOCK_WALLET.format(cli, passphrase, WALLET_LOCK_TIMEOUT_SEC)
    return subprocess.check_output(command, stderr=subprocess.STDOUT).decode(DEFAULT_DECODE)
            
def sendToAddress(cli, address, amount):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        address (str): Address to be used for sending.
        amount (int): Amount of coins to be sent.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_SEND_TO_ADDRESS.format(cli, address, amount)
    return subprocess.check_output(command, stderr=subprocess.STDOUT).decode(DEFAULT_DECODE).strip()

def getTotalBalance(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_GET_BALANCE.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE)

def listUnspent(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_LIST_UNSPENT.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE)
    
def getMasternodeOutputs(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_MASTERNODE_OUTPUTS.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE)
    
def generateMasternodeKey(cli):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_MASTERNODE_GENKEY.format(cli)
    return subprocess.check_output(command).decode(DEFAULT_DECODE).strip()

def masternodeStartAlias(cli, alias):
    """Wrapper function for the relevant RPC function call.
    
    Args:
        cli (str): Full path to cli binary associated with coin.
        alias (str): Alias associated with masternode to be started.
        
    Returns:
        String: String containing the command output.        
    """
    command = CLI_MASTERNODE_START_ALIAS.format(cli, alias)
    return subprocess.check_output(command).decode(DEFAULT_DECODE).strip()

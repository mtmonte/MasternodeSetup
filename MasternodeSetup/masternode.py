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

from . import vps
from . import core

import argparse
import configparser

CONFIG_FILENAME = os.path.join(os.path.dirname(__file__), "conf", "config.ini")

DESCRIPTION = "End to end script to setup a masternode"

ROOT_USER = "root"

def getConfig():
    """Parse configuration file.
    
    Returns:
        dict: Dictionary containing the options parsed.
    """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    
    return config

def begin(args):
    """Wrapper function that starts the application with the given arguments.
    
    Args:
        args (obj): Object containing the command line arguments parsed.
    """
    try:
        # Parse file configuration
        config = getConfig()

        # Ensure all local requirements met (e.g. wallet installed)
        core.checkPrerequisites(config)
    
        # Setup VPS - Update packages, install binaries
        vps.setup(args.vps, ROOT_USER, args.password, config)
    
        # Setup masternode locally
        core.setup(args.vps, ROOT_USER, args.password, args.name, config)
        
    except Exception as e:
        print("Masternode setup failed. Reason: {0}.".format(str(e)))  
        raise e
    
def setup():
    """Program entrypoint. This function will parse all program arguments and start the application.
    """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    
    parser.add_argument("--name", action="store", required=True, help="The name to be given to the masternode")
    parser.add_argument("--vps", action="store", required=True, help="The IP address of the VPS server to be used")
    parser.add_argument("--password", action="store", required=True, help="The root password for the VPS provided")
    
    args = parser.parse_args()    
    begin(args)
    
if __name__ == "__main__":
    setup()
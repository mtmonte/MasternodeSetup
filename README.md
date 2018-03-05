# End-to-end Masternode Setup

## About

This project was created to facilitate the setup of masternodes in the cryptocurrency community.  Many coins today adopt a masternode PoS rewards system that require users to setup a VPS capable of running the blockchain.  Several guides exist today the "walk-through" the installation and setup process of these systems.  Unfortunately, they are error-prone, time-consuming, and require users to be familiar with UNIX type operating systems.

The purpose of this project is to facilitate this process as much as possible and to provide a true "1-click" system that sets up a masternode for the user.  The is hands down the simplest and most convenient way to setup a masternode.

## Applications

This project was created with [Cosmos Coin](cosmoscoin.co) in mind; however, all coin specific settings are kept in configuration files that make it easy for the community to configure the application to work on other coins as well.  As many masternode projects derive from the same source, we imagine that the existing code will work in most cases and only changes to the configuration files will be required.  Please refer to this [guide](https://docs.google.com/document/d/103liXiffv1UcEeT0seBObG7ALEhEJhCLtHbU6pHc0uA/edit?usp=sharing) for more information on each of the steps taken by this utility when drawing comparisons to other coins.

## Features

- The easiest and most convenient way to setup a masternode.
- Check existing masternode configuration and update to the latest (not available yet).

## Prerequisites

The following is required to run this application:
- [Python 3.x](https://www.python.org/downloads/)
- An local wallet installation.
- An existing [VPS](https://www.vultr.com/?ref=7302072) instance running Ubuntu 16.04.
- A set of environment variables that indicate the wallet installation and user directories.

**Note:** The local wallet and VPS daemon must be stopped before starting this application.

## Summary

This application uses a set of RPC calls to setup the masternode transactions required while opening up an SSH connection to configure the VPS instance.

**Note:** All coin transaction are contained within the local wallet.  As a result, your coins will always be under your control.  If any of the steps below fail for **any** reason, your coins will **NOT** be lost.

The following steps are carried out by this application:

1. Verify that the specified prerequisites are met.
1. Setup VPS instance:
   1. Confirm that the masternode daemon is not running on the VPS.
   1. Update tools on VPS (apt-get upgrade, etc)
   1. Install the latest release of the wallet published in the coin's github page.
   1. Create a masternode user with the coin's name (to be used to run the daemon).
1. Setup local wallet:
   1. Confirm that wallet conf file contains rpcuser / rpcpassword entries, create them if necessary.
   1. Start local wallet in daemon mode.
   1. Wait for local wallet to be in sync.
   1. Verify balance against collateral requirement.
   1. Send collateral to masternode address (prompts for password, if needed).
      1. **Note:** This will use any available funds.
   1. Query masternode output associated with collateral.
   1. Query for masternode key.
   1. Create the VPS conf file and copy it to VPS.
   1. Start VPS masternode daemon.
   1. Setup local masternode conf file with above values.
   1. Start masternode by alias.

The following is currently **not** performed by this utility (may be included in future release):

1. Create / start a VPS instance.
1. Specify source address of coins.
1. Key based authentication to VPS.
1. Configure ipbanlist / firewall on VPS.

# Contributions

This guide was developed by the [Cosmos](cosmoscoin.co) community.  The best way to support us is to spread the word about our coin and to join our community.  

[Bitcointalk ANN](https://bitcointalk.org/index.php?topic=2634321.0)  
[Discord](https://discord.gg/Kz9u4d2)  
[Reddit](https://www.reddit.com/r/COSMOSCOINofficial/)  
[Facebook](https://www.facebook.com/groups/1798549983782929/)

If you still feel like you must send a donation, any amount is welcome:

`CMOS: CURWPBmxZEN1TCVH9F2EzoW14xLreyVMzR`

# Cosmos masternode setup

The following section is specific to the setup of masternodes for [Cosmos Coin](cosmoscoin.co).  To setup a masternode, follow the steps below on the primary computer containing the Cosmos wallet.

## Virtual Private Server (VPS)

You must have a VPS service set up before proceeding.  This server should be running Ubuntu 16.04 and should contain a swap file of at least 6 GB.  Refer to this [guide](https://www.digitalocean.com/community/tutorials/how-to-add-swap-space-on-ubuntu-16-04) for more information on how to check or increase the swap file.  If you don't have an existing VPS, consider [Vultr](https://www.vultr.com/?ref=7302072) as they have reasonable prices and are very easy to use.

To create a swap file, please run the following commands on the Ubuntu server.

**Note:** To be automated in a future release.

```
fallocate -l 6G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo -e "/swapfile   none    swap    sw    0   0 \n" >> /etc/fstab
```

## Environment variables

You must set the `COSMOS_HOME` and `COSMOS_USER` environment variables before you begin.  The `COSMOS_HOME` variable should point to the Cosmos installation directory, the `COSMOS_USER` should point to the directory containing the configuration files.

Example:

```
COSMOS_HOME=C:\Program Files\Cosmos
COSMOS_USER=C:\Users\Administrator\AppData\Roaming\Cosmos
```

## Installation

This application leverages the python `pip` distribution system.  With python 3.x installed, open a new terminal or command prompt window and install the package as follows:

**Important:** Ensure that this software is installed from trusted sources **only**.  Do **NOT** download this from any sites other the the ones listed below.  You don't want to become a victim of a phishing scam.  Stay safe!

**Note:** Ensure that python is in your operating system's `PATH` before proceding.

```
pip install Cosmos-Coin-Masternode-Setup
```

After the installation is completed, you should be able to run the script as follows:

```
C:\Users\Administrator>cosmos-masternode-setup.exe --help
usage: cosmos-masternode-setup [-h] --name NAME --vps VPS --password PASSWORD

End to end script to setup a masternode

optional arguments:
  -h, --help           show this help message and exit
  --name NAME          The name to be given to the masternode
  --vps VPS            The IP address of the VPS server to be used
  --password PASSWORD  The root password for the VPS provided
```

## Setup

**Important:** Your wallet must be **closed** before you continue.

1. Note down your VPS's IP address and password.
1. Ensure you meet the required 10,000 coin collateral.  This does not have to be in a single cmos address.
1. Open a terminal or command prompt window and start the utility with the following arguments:

   **Note:** The masternode name should **not** contain any spaces.

   Example:

   ```
   C:\Users\Administrator>cosmos-masternode-setup.exe --name <Name for node> --vps <vps IP address> --password <VPS password>
   ```

1. Wait for the utility to finish.  If your wallet is encrypted, it will ask for your password before sending the masternode collateral.

   **Important:** Should anything **fail**, your coins are 100% safe as the address used will be part of your wallet.  Look at the error message displayed and fix and issues as required.
   
1. After the utility finishes, open your wallet and verify that the masternode is present.  Verify that your new node is enabled.  Although the utility attempts to start the node, you may still need to hit the `START MISSING` command before it is reflected.

   [Example](https://imgur.com/a/KM2VT)

1. That's it!  You're done!
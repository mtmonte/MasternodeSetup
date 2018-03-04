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

from setuptools import setup

setup(name="Cosmos Coin Masternode Setup",
      version="1.1.0",
      description="End to end script to setup a masternode",
      url="https://github.com/mtmonte/MasternodeSetup",
      author="mtmonte",
      author_email="cosmos.mtmonte@gmail.com",
      keywords="bitcoin cosmos coin crypto cryptocurrency masternode",
      license="MIT",
      packages=["MasternodeSetup"],
      python_requires=">=3.3.0",
      install_requires=["paramiko"],
      entry_points={"console_scripts": ["cosmos-masternode-setup=MasternodeSetup.command_line:main"]},
      include_package_data=True,
      zip_safe=False)      
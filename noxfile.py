# We include this so that we can use the `libs` module in the `tests` directory
import sys
sys.path.append('tests')

from lib import *

import os
import nox
import time
import shutil
import pathlib
import subprocess

PACKAGE_BUILT = False

@nox.session()
def build(session):
    global PACKAGE_BUILT
    PACKAGE_BUILT = True
    session.run("pdm", "build", )

@nox.session(python=['pypy3', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12' ])
def tests(session):
    global PACKAGE_BUILT

    session.run("pdm", "install", "-d")

    session.run("pdm", "run", "pytest", "--log-cli-level=WARN", "-s")

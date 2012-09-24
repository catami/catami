'''
This is the main import file to create a common namespace.
'''
import logging
import logging.config
import ConfigParser
import src.importTools as importTools
from Force.models import *
import os

#==================================================#
# Initialize the Django settings etc
#==================================================#

ROOT=os.getcwd()
SRC=ROOT+'/src'
TEST=ROOT+'/test'
#==================================================#
# Open the config file and read contents
#==================================================#
config = ConfigParser.ConfigParser()  #For general configs
config.readfp(open(ROOT+'/catamiPortalConfigs.cfg'))

logging.config.fileConfig(ROOT+'/logging.cfg') # For logging configs
logging=logging.getLogger('catamiPortal')




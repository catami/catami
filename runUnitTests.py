import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'catamiPortal.settings'
from django.test.utils import setup_test_environment
setup_test_environment()
import catamiWebPortal

#==================================================#
# Add Tests to start here
#==================================================#

execfile('test/importToolsUnitTest.py')

"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import os
from paramiko import AuthenticationException

from django.test import TestCase
from mock import Mock
from features import FeaturesErrors
import features
from features.RunScriptTool import RunScriptTool
from dbadmintool.administratorbot import Robot
import logging
logger = logging.getLogger(__name__)


class RunScriptTest(TestCase):
    """Test for the RunScriptTool"""

    def setUp(self):

        mock_user = 'test'
        mock_password = 'test'

        self.server = Mock()
        self.rst = RunScriptTool()

        # for bender.check_sum_file method
        self.bender = Robot()

    def test_write_pbs_script(self):
        """Check that the code writes the correct pbs script"""
        self.rst.write_pbs_script()
        mock_write_check = self.bender.check_sum_file(self.rst.run_file)
        mock_fixture_check = self.bender.check_sum_file(
            'features/fixtures/mock_pbs_script.pbs')
        self.assertTrue(mock_fixture_check == mock_write_check)

    def test_push_pbs_script_to_server(self):
        # Test normal operation
        self.assertIsNone(self.rst.push_pbs_script_to_server(self.server))

    def test_server_calls_push_pbs_script_to_server(self):
        """Test to make sure that put and execute are called at least once"""
        self.rst.push_pbs_script_to_server(self.server)
        self.server.put.assert_called_once_with('catami.pbs')
        self.server.close.assert_called_once_with()

    def test_server_put_push_pbs_script_to_server(self):
        # Test that user name or possword is incorrect
        # force the username and/or password to be incorrect
        self.server.put.side_effect = AuthenticationException("Testing")

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.ConnectionError,
        # self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!
        try:
            self.rst.push_pbs_script_to_server(self.server)
        except features.FeaturesErrors.ConnectionError as e:
            connection_error_occured = True

        self.assertTrue(connection_error_occured)

    def test_server_execute_push_pbs_script_to_server(self):
        """Test to see that the correct exception is raised

         if we cant kick pbs"""

        # Force a startjob fail.
        self.server.execute.side_effect = Exception("Testing")

        #!!!!!!!!!!!!!!!!!!!!
        # THE FOLLOWING LINE DOES NOT WORK
        # self.assertRaises(features.FeaturesErrors.
        # ConnectionError,self.rst.push_pbs_script_to_server(self.server))
        #--------------------
        # THE FOLLOWING IS A WORKAROUND
        #!!!!!!!!!!!!!!!!!!!!

        try:
            self.rst.push_pbs_script_to_server(self.server)
        except features.FeaturesErrors.ConnectionError as e:
            execute_error_occured = True

        self.assertTrue(execute_error_occured)

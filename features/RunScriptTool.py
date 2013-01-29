__author__ = 'marrabld'

import logging
import datetime
from features import FeaturesErrors

logger = logging.getLogger(__name__)


class RunScriptTool():
    """ This tool is designed to generate the pbs script for queoing libCluster
    http://www.clusterresources.com/products/torque/docs10/a.hlicense.txt

    """

    def __init__(self, username='password', password=''):
        """Default class parameters for the runscript"""

        #====================
        # PARAMETERS FOR THE RUN SCRIPT
        #====================
        self.pbs_workgroup = 'partner464'  # workgroup for CATAMI

        #====================
        # JOB QUEUE TYPE
        #--------------------
        # http://portal.ivec.org/docs/PBS_Pro_on_Epic
        # available are routequeue,largeq,mediumq,smallq,
        # longq,copyq,debugq,testq
        #====================
        self.job_queue = 'routequeue'
        self.wall_time = datetime.time(12, 0, 0)  # Max job time
        self.memory = 23  # required RAM in gigabytes
        self.num_nodes = 1
        self.num_cpus = 12
        self.scratch_directory = '/scratch/' + self.pbs_workgroup + '/catami'
        self.run_file = 'catami.pbs'  # default script name
        self.library = 'libFeature'  # ie clustering, features etc

        #====================
        # PARAMETERS FOR THE RUN SERVER
        #====================
        self.server_ip = 'epic.ivec.org'
        self.server_username = username
        self.server_password = password

    def write_pbs_script(self):
        """Writes the parameters to a pbs script

        queues a job on a pbs server"""

        f = open(self.run_file, 'w')

        logger.debug('Writing pbs script :: ' + self.run_file)

        f.write(
            '#!/bin/bash' + '\n'
            '# pbs file generated by catamiPortal' + '\n'
            '#PBS -W group_list=' + self.pbs_workgroup + '\n'
            '#PBS -q ' + self.job_queue + '\n'
            '#PBS -l walltime=' + str(self.wall_time) + '\n'
            '#PBS -l select=' + str(self.num_nodes) + ':ncpus=' +
            str(self.num_cpus) + ':mem=' + str(self.memory) + 'gb'
            '\n'
            'cd ' + self.scratch_directory + '\n'
            '\n'
            'echo \"Running ' + self.library + '\"\n'
        )

        f.close()

    def push_pbs_script_to_server(self, server=object, password='',
                                  start_job=True):
        """
        Pushes the run script to the server and initiate the job

        :param password: Password for the server
        :return:
        """

        # TODO : Figure out what files to push with the script

        # SCP over the pbs sript
        logger.debug('copying file :: ' +
                     self.run_file + ' to :: ' +
                     self.server_ip)

        try:
            server.put(self.run_file)
        except:
            logger.error('Failed to PUT :: ' +
                         self.run_file +
                         ' to server :: ' +
                         self.server_ip)

            raise FeaturesErrors.ConnectionError('Failed to put ',
                'Failed to PUT :: ' +
                self.run_file +
                'to server :: ' +
                self.server_ip)

        if start_job:
            # Queue the job
            logger.debug('Sending job request')
            try:
                server.execute('qsub ' + self.run_file)
            except:
                logger.error('Failed to submit job :: ' + self.run_file)
                raise FeaturesErrors.ConnectionError('Failed to start ',
                    'Failed to submit job :: ' +
                    self.run_file)

        server.close()

import json
import os
import cPickle as pickle
import random
import scipy
import string
import tarfile
from django.core import serializers

__author__ = 'marrabld'

import logging
import datetime
from features import FeaturesErrors

logger = logging.getLogger(__name__)

class DeployJobTool():
    """ This tool is designed build launch libcluster or libfeature on Epic

    or any computer running Torque and libcluster/libfeature.  We put all of the
    data here and only write the data to file that the particular lib needs.  I.e.
    try and make the tool agnostic to the lib its running.

    Example use:

    import features.RunScriptTool as DJT
    a = DJT.DeployJobTool()
    a.image_primary_keys = ['00000001','00000002'] #dummpy keys
    a.write_json_file()
    a.write_rand_numpy_array_to_disk()
    a.compress_files()
    """

    def __init__(self):
        """ default class parameters for the job"""

        #====================
        # PARAMETERS FOR LIBCLUSTER/LIBFEATURE
        #====================

        self.cluster_granularity = 1
        self.verbose_output = True
        self.nthreads = 1
        self.dimensionality = 20
        self.algorithm = 'BGMM'
        # The images we would like to cluster/feature
        self.image_primary_keys = []
        self.user_name = 'Anon'

        self.job_id = self.id_generator()

        logger.debug('job_id is :: ' + self.job_id)
        self.job_dir = '/tmp/CATAMI/features/' + self.user_name + '/' + self.job_id
        os.makedirs(self.job_dir)

        #TODO : need to parse user id from the front end of the person that is logged in

        # This will be a list of deployments after querying based on image list
        # might leave this out for now 06/02/13 Dan M
        # deployment_information = []

    def write_json_file(self):

        parameter_dict = {'cluster_granularity' : self.cluster_granularity,
                          'verbose_output' : self.verbose_output,
                          'nthreads' : self.nthreads,
                          'dimensionality' : self.dimensionality,
                          'algorithm' : self.algorithm,
                          'image_primary_keys' : self.image_primary_keys}


        f = open(self.job_dir + '/features.json','wb')

        logger.debug('Writing features.json to disk at location :: ' + self.job_dir)
        f.write(json.dumps(parameter_dict))

    def write_rand_numpy_array_to_disk(self, dim=(1,20)):
        """This is mostly for testing and debugging

        This will generate a random vector that will simulate the features vector
        dim is the require dimensions r,c
        Returns : numpy.array
        """

        for im in self.image_primary_keys:
            if dim[0] == 1:
                feature = scipy.rand(dim[1])
            else:
                feature = scipy.rand(dim[0],dim[1])

            pickle.dump(feature, open(self.job_dir + '/' + im + '.p','wb'))

    def compress_files(self,fname='features', **kwargs):
        """

        do_zip [True] :: compress or not.
        compression_type [gz] :: gz or bz

        :param kwargs:
        :return:
        """

        compression_type = kwargs.get('compression_type', 'gz')
        do_zip = kwargs.get('do_zip', True)

        tar = tarfile.open(self.job_dir +
                           '/' +
                           fname +
                           '.tar.' +
                           compression_type,
            'w:' +
            compression_type)

        tar.add(self.job_dir + '/features.json', arcname='/features.json')
        for im in self.image_primary_keys:
            tar.add(self.job_dir + '/' + im + '.p', arcname=im + '.p')

        tar.close()



    #def push_files_to_server(self):
    #    pass

    def id_generator(self, size=12, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for x in range(size))


class RunScriptTool():
    """ This tool is designed to generate the pbs script for queuing libCluster
    http://www.clusterresources.com/products/torque/docs10/a.hlicense.txt

    """

    def __init__(self, username='user', password=''):
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
        self.library = 'libCluster'  # ie clustering, features etc

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

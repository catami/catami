from distutils.core import setup
from DistUtilsExtra.command import *

import glob
import os

def gen_data_files(*dirs):
    """build the data file structure to copy over"""
    results = []

    for src_dir in dirs:
        for root,dirs,files in os.walk(src_dir):
            results.append((root, map(lambda f:root + "/" + f, files)))
    print results
    return results

setup(name="catamiportal",
      version="0.10",
      description='CATAMI web portal code',
      author="Dan Marrable",
      author_email="d.marrable@ivec.org",
      url="https://launchpad.net/~catami",
      license="zlib",
      package_dir = {'':''},
      packages = ['Force','staging'],

      scripts=['startCatamiWebPortal.py','catami_web_portal.py','runUnitTests.py','manage.py'],
      data_files = gen_data_files('./', 'Force','assests','admin','staging','log'),

      cmdclass={"build":  build_extra.build_extra, }
)

print 'DONE'

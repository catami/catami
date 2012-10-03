from distutils.core import setup
from DistUtilsExtra.command import *

import glob

setup(name="pymi",
      version="0.1",
      description='A simple image processing program written for medical imaging undergraduate students to explore DSP of images without having to learn programming.',
      author="Dan Marrable",
      author_email="marrabld@gmail.com",
      url="https://launchpad.net/~marrabld",
      license="GNU General Public License Version 3 (GPLv3)",
      package_dir = {'':'src'},
      scripts=['pyMi.run'],
      py_modules=['errorHandler','imageFuncs','loadGui','mainGui','main','mplWidget','aboutGui','helpGui'],
      data_files=[('/usr/share/applications',['pymi.desktop']),
                  ('icons', ['icons/pymi.png','icons/i_document-open.png','icons/i_document-save.png','icons/i_help-contents.png','icons/i_help-about.png','icons/i_view-refresh.png','icons/document-open.png','icons/document-save.png','icons/help-contents.png','icons/help-about.png','icons/view-refresh.png']),
                  ('Images',['src/Images/DALEC.jpg','src/Images/greyTux.jpg'])
      ],
      cmdclass={"build":  build_extra.build_extra, }
)


#                  ('/opt/extras.ubuntu.com/pymi',['pyMi.run']),
#      packages=[''],

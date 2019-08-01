'''

@author: Umesh babar
@summary: Setup Script for remote_host_file_sync_service
'''
import os, sys, re
from codecs import open


try:
    from setuptools import setup, find_packages
except ImportError:
    print ("setuptools is needed to run this file")
    print ("Try -- 'sudo pip install setuptools'")
    print ("Exiting ..")
    sys.exit(1)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open('remote_host_file_sync_service'+ os.sep +'__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('Cannot find version information')

setup(
    name                = "remote_host_file_sync_service",
    version             = version,
    author              = "Umesh Babar ",
    author_email        = "umeshbabar27@gmail.com",
    description         = ("This is tool for Deploy and configuration of file sync on Remote Host"),
    keywords            = "remote_host_file_sync_service",
    packages            = ['remote_host_file_sync_service','remote_host_file_sync_service.api'],
    long_description    = read('README.md'),
    install_requires    = [required_pkg.strip() for required_pkg in open('requirements.txt')],
    # data_files = [("/etc",["remote_host_file_sync_service/logging.conf"])],
    # package_data = {
    #     # If any package contains *.txt or *.rst files, include them:
    #     #'': ['*.txt', '*.rst'],
    #     # And include any *.msg files found in the 'hello' package, too:
    #     '': ['*.conf'],
    # },
    include_package_data= True,
    scripts             = ['remote_host_file_sync_service/rhfs_app'],

)

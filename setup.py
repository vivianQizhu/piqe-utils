from setuptools import setup, find_packages

from piqe_utils import __version__

setup(
    name="piqe-utils",
    version=__version__,
    author="PIQE Libraries Team",
    author_email="portfolio-integration-qe@redhat.com",
    description="PIQE OpenShift Python Libraries.",
    url="https://github.com/piqe-test-libraries/piqe-utils.git",
    packages=find_packages(),
    install_requires=[
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
    ],
)

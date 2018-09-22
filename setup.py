from setuptools import setup

setup(
    name='pys3browser',
    version='1.0.0',
    packages=['pys3browser'],
    install_requires=['Flask', 'humanfriendly', 'boto3'],
    url='https://github.com/amjad489/pys3browser',
    license='',
    author='amjad489',
    author_email='amjadhussain3751@gmail.com',
    description='Simple web based interface for browsing AWS S3 bucket'
)

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = open('README.rst').read()

setup(
    name='crossbarhttprequests',
    packages=['crossbarhttp'],
    version='0.1.6',
    description='This is a library for connecting to Crossbar.io HTTP Bridge Services using python-requests.',
    author='Yomi Daniels',
    license='MIT',
    author_email='yomid4all@gmail.com',
    url='https://github.com/ydaniels/crossbarhttprequests',
    long_description=readme,
    keywords=['wamp', 'crossbar', 'requests'],
    install_requires=['requests', 'requests_futures'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities',
    ],
)

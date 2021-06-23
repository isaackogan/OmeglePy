try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='OmeglePy',
      version='1.07',
      description='Python API for Omegle Web-Chat',
      long_description='Python API for Omegle Web-Chat. Usage: https://github.com/isaackogan/OmeglePy',
      author='Elia Scotto maintained by Isaac Kogan',
      author_email='isaacikogan@gmail.com',
      url='https://github.com/elias94/pyomegle',
      license='MIT',
      packages=['pyomegle'],
      install_requires=['mechanize'],
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Communications :: Chat',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP :: Browsers'
      ],
      zip_safe=False
)

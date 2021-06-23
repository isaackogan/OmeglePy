try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
  name = 'OmeglePy',        
  packages = ['OmeglePy'],  
  version = '1.0',     
  license='MIT',       
  description = 'Interact with the Omegle API',   
  author = 'Isaac Kogan (Originally Elia Scotto)',                  
  author_email = 'isaacikogan@gmail.com',      
  url = 'https://github.com/isaackogan/OmeglePy',   
  download_url = 'https://github.com/isaackogan/OmeglePy/archive/refs/tags/v_1.0.tar.gz',  
  keywords = ['OmeglePy', 'Omegle', 'Omgle-Bot', 'Bot'],  
  install_requires=[            
          'mechanize',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Communications :: Chat',
    'Operating System :: POSIX',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.8',
  ],
  zip_safe=False
)

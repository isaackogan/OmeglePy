from setuptools import setup, find_packages

setup(
    name='OmeglePy',
    packages=find_packages(),
    version='2.2',
    license='MIT',
    description='Interact with the Omegle API',
    author='Isaac Kogan',
    author_email='isaacikogan@gmail.com',
    url='https://github.com/isaackogan/OmeglePy',
    download_url='https://github.com/isaackogan/OmeglePy/archive/refs/tags/v_2.2.tar.gz',
    keywords=['OmeglePy', 'Omegle', 'Omgle-Bot', 'Bot'],
    install_requires=[
        'asyncio', 'aiohttp'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',  # "3 - Alpha", "4 - Beta", "5 - Production/Stable"
        'Intended Audience :: Developers',  # Define that your audience are developers
        'Topic :: Communications :: Chat',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',  # Again, pick a license
        'Programming Language :: Python',  # Specify which Python versions that you want to support
        'Programming Language :: Python :: 3.8',
    ],
    zip_safe=False
)

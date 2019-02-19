from setuptools import setup


setup(
    name='Daemonize',
    version='0.0.1',
    py_modules=['cli'],
    entry_points={
        'console_scripts': [
            'daemonize=cli:main',
        ],
    }
)

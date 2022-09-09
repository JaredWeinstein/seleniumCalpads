from setuptools import setup, find_packages

setup(
    name='seleniumCalpads',
    version='1.0',
    packages=find_packages(include=['src', 'src.*']),
    install_requires=[
        'selenium',
        'customtkinter'
    ],
    entry_points={
        'console_scripts': ['get_calpads=src.main:main']
    },
    package_data={'': ['*.json', '*.bat']}
)

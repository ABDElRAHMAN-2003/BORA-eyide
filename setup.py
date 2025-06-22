from setuptools import setup, find_packages

setup(
    name="crewai-chatbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "crewai>=0.16.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        'console_scripts': [
            'crewai-chatbot=src.main:main',
        ],
    },
) 
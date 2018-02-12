from setuptools import setup, find_packages


setup(
    name='chatterbox.py',
    version='0.0.1',
    description='Python library for Kakaotalk chatbot',
    long_description='Help to make chatbot using a state machine.',
    author='JungWinter',
    author_email='wintermy201@gmail.com',
    url='https://github.com/JungWinter/chatterbox',
    packages=find_packages(exclude=('tests', 'examples', 'concept')),
    py_modules=['chatterbox'],
    install_requires=['redis'],
    tests_require=['pytest' 'pylint', 'tox', 'pytest-cov'],
    include_package_data=True,
    license='MIT'
)

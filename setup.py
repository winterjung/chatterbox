from setuptools import setup, find_packages


with open('README.rst') as fp:
    long_description = '\n' + fp.read()

setup(
    name='chatterbox.py',
    version='0.0.1',
    description='Python library for Kakaotalk chatbot',
    long_description=long_description,
    author='JungWinter',
    author_email='wintermy201@gmail.com',
    url='https://github.com/JungWinter/chatterbox',
    packages=find_packages(exclude=('tests',)),
    py_modules=['chatterbox'],
    install_requires=[],
    tests_require=["pytest", "pylint", "tox", "pytest-cov"],
    include_package_data=True,
    license='MIT'
)

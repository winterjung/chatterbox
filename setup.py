from setuptools import setup, find_packages


setup(
    name='chatterbox',
    version='0.0.1',
    description='Python library for Kakaotalk chatbot',
    long_description='long_description',
    author='JungWinter',
    author_email='wintermy201@gmail.com',
    url='https://github.com/JungWinter/chatterbox',
    packages=find_packages(exclude=('tests',)),
    install_requires=[],
    tests_require=["pytest", "pylint", "tox", "pytest-cov"],
    include_package_data=True,
    license='MIT'
)

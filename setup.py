from setuptools import setup

setup(
    name='polarizer_py',
    version='0.1.0',
    packages=['polarizer_py'],
    install_requires=["pyyaml", "rx", "pyxb", "toolz", "websockets"],
    url='https://github.com/RedHatQE/polarizer-py',
    license='Apache-2.0',
    author=['Sean Toner','Jan Stavel'],
    author_email=['stoner@redhat.com','jstavel@redhat.com'],
    description='Metadata decorator for polarizer services'
)

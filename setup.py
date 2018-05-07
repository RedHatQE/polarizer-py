from setuptools import setup

setup(
    name='polarizer_py',
    version='0.1.0',
    packages=['polarizer_py'],
    install_requires=["pyyaml", "rx", "pyxb", "toolz", "websockets"],
    url='https://github.com/rarebreed/polarizer-py',
    license='Apache-2.0',
    author='Sean Toner',
    author_email='stoner@redhat.com',
    description='Metadata decorator for polarizer services'
)

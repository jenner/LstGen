import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.md')) as f:
    CHANGES = f.read()
long_description = README + "\n\n" + CHANGES
try:
    import pypandoc
    long_description = pypandoc.convert(long_description, 'rst', format='md')
except(IOError, ImportError):
    pass
requires = [
    'lxml',
    'requests',
]
testing_extras = requires + [
    'nose',
    'coverage',
]

setup(name='LstGen',
    version='0.4.0',
    description='LstGen',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Code Generators"
    ],
    author='Igor Stroh',
    author_email='igor.stroh@rulim.de',
    url='http://github.com/jenner/LstGen',
    keywords='lohnsteuer code generator cli',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    extras_require = {
        'testing': testing_extras,
    },
    entry_points="""\
    [console_scripts]
    lstgen = lstgen.cli:main
    """
)

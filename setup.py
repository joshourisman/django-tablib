#!/usr/bin/env python

from distutils.core import setup


description = "A wrapper around Kenneth Reitz' tablib to work with Django " \
    "models."

VERSION = '3.1.1'

setup(
    name='django-tablib',
    version=VERSION,
    author='Joshua Ourisman',
    author_email='josh@joshourisman.com',
    url='https://github.com/joshourisman/django-tablib',
    description=description,
    long_description=description,
    license='MIT',
    platforms=['any'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    packages=['django_tablib', ],
    package_data={'django_tablib': ['templates/tablib/*', 'admin/*'], },
    install_requires=['tablib', 'six'],
)

from setuptools import setup, Extension

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pytimeset',
    version='0.5.10',
    packages=['timeset'],
    url='https://github.com/GFlorio/pytimeset',
    license='MIT',
    author='Gabriel Florio',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='gabriel@gabrielflorio.com',
    description='Defines sets and intervals to work with time, and provides arithmetic operations '
                'for them. Uses Cython extensions for performance.',
    ext_modules=[Extension('timeset.timeset', ['timeset/timeset.c'])],
    package_data={'timeset': ['timeset.pyi', 'py.typed']},
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)

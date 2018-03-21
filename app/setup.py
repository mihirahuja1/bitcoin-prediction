from setuptools import setup

setup(
    name='mlsite',
    packages=['mlsite'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Keras',
        'numpy',
        'tensorflow',
        'gunicorn',
        'h5py',
        'scikit-learn'
    ],
)
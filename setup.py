from setuptools import setup, find_packages

setup(
    name="decision_tree_manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "markdown",
    ],
    entry_points={
        'console_scripts': [
            'decision_tree_manager=decision_tree_manager.main:main',
        ],
    },
    include_package_data=True,
    package_data={
        'decision_tree_manager': ['utils/*.otf'],
    },
)
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="samplify-QZDL", # Replace with your own username
    version="0.0.1",
    author="Samuel Culpepper",
    author_email="library@samuelculpepper.com",
    description="The sample retrieval engine, powered by WhoSampled",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qzdl/samplify",
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    entry_points="""
     [console_scripts]
     samplify = samplify.samplify:main
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPL 3.0 License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)

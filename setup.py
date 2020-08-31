import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="samplify-QZDL", # Replace with your own username
    version="0.0.1",
    author="Samuel Culpepper",
    author_email="info@samuelculpepper.com",
    description="The sample retrieval engine, powered by WhoSampled",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/qzdl/samplify",
    packages=setuptools.find_packages('src', 'src/tools'),
    package_dir={'': 'src'},
    install_requires=[
        "BeautifulSoup4",
        "objectpath==0.6.1",
        "fuzzywuzzy==0.17.0",
        "python-Levenshtein==0.12.0",
        "spotipy @ git+https://github.com/qzdl/spotipy.git",
    ],
    # dependency_links=[
    #     "git+https://github.com/qzdl/spotipy.git", # setuptools can suck it
    # ],
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

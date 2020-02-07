import setuptools

with open("README.org", "r") as fh:
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
    packages=setuptools.find_packages('src' 'platforms'),
    package_dir={'': 'src'},
    install_requires=[
        "beautifulsoup4==4.8.0",
        "fuzzywuzzy==0.17.0",
        "google-api-python-client==1.7.11",
        "google-auth==1.6.3",
        "google-auth-httplib2==0.0.3",
        "google-auth-oauthlib==0.4.0",
        "objectpath==0.6.1",
        "python-Levenshtein==0.12.0",
        "requests==2.22.0",
        "rsa==4.0",
        "six==1.12.0",
        "soupsieve==1.9.3",
        "urllib3==1.25.3",
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

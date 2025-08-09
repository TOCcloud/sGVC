from setuptools import setup, find_packages

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="sgvc",
    version="1.0.0",
    author="Kozosvyst Stas",
    author_email="dev@sxscli.com",
    description="Simple GitHub Version Control library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StasX-Official/sGVC",
    packages=find_packages(),
    install_requires=[
        "requests",
        "packaging"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)

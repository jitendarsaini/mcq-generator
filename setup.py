# pip install -r requirements.txt

from setuptools import find_packages, setup
 
setup(
    name="mcq-generator",
    version="0.0.1",
    author="jitendra",
    author_email="jitendarsaini2580@gmail.com",
    packages=find_packages(),
    install_requires=["groq","langchain","streamlit","python-dotenv","pyPDF2"]
)
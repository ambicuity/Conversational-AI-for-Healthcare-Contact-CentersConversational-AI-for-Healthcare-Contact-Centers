"""Setup configuration for Healthcare Conversational AI Platform."""

from setuptools import setup, find_packages

setup(
    name="healthcare-conversational-ai",
    version="1.0.0",
    description="Enterprise Conversational AI Platform for Healthcare Contact Centers",
    author="Healthcare AI Team",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "google-cloud-dialogflow-cx>=1.30.0",
        "google-cloud-aiplatform>=1.38.0",
        "google-generativeai>=0.3.1",
        "google-cloud-pubsub>=2.18.4",
        "google-cloud-logging>=3.8.0",
        "google-cloud-secret-manager>=2.16.4",
        "flask>=3.0.0",
        "requests>=2.31.0",
        "pydantic>=2.5.0",
        "celery>=5.3.4",
        "redis>=5.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-mock>=3.12.0",
            "pylint>=3.0.3",
            "black>=23.12.1",
        ]
    },
)

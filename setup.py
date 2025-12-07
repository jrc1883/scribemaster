from setuptools import setup, find_packages

setup(
    name="scribemaster",
    version="0.4.0",
    description="AI-Powered Book Writing Suite - Context-aware, multi-agent book creation",
    author="jrc1883",
    url="https://github.com/jrc1883/scribemaster",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "typer",
        "openai",
        "python-dotenv",
        "pydantic",
        "pydantic-settings",
        "beautifulsoup4",
        "requests",
        "markdown",
        "fpdf",
        "tenacity",
        "anthropic",
        "google-generativeai",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "scribemaster=libriscribe.main:app",
            "libriscribe=libriscribe.main:app",  # Backward compatibility
        ],
    },
    python_requires=">=3.8",
)

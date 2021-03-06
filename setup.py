from setuptools import setup

REQUIREMENTS_TESTING = [
    "pytest",
]

REQUIREMENTS_DEVELOPMENT = [
    "ipykernel",
    "jupyter",
    "jupyter-client",
    "jupyter-console",
    "jupyter-core",
    "pytest",
]

setup(
    name="ches-data-analysis",
    python_requires=">=3.9.0",
    install_requires=[
        "darker",
        "isort",
        "graphviz",
        "plotly",
        "pyvis",
        "streamlit",
        "streamlit_agraph"
        "tabula-py",
    ],
    tests_require=REQUIREMENTS_TESTING,
    extras_require={
        "testing": REQUIREMENTS_TESTING,
        "development": REQUIREMENTS_DEVELOPMENT,
    },
)

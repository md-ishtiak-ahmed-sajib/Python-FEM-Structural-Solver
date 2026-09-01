# Install and run the project

[Project home](../../README.md) · [Documentation map](../README.md) · [Section guide](README.md)


You need Python 3.12 and the project folder. The tested setup is Windows with Python 3.12.10. No GPU, cloud account or API key is needed.

## Install on Windows

Open PowerShell inside the project folder. Run these commands one at a time:

~~~powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.lock
.\.venv\Scripts\python -m pip install -e . --no-deps
.\.venv\Scripts\python -m streamlit run app.py
~~~

The first command creates a **virtual environment**: a separate folder of Python tools for this project. The lock file lists the exact package versions used in the checked setup. The third command connects the local source code to that environment.

Open [the local app](http://127.0.0.1:8501) after the server starts. Keep the PowerShell window open while using it. Press Ctrl+C in that window to stop it.

After installation, you can double-click [run-local.cmd](../../run-local.cmd).

## Internet and local use

Installation needs internet unless you already have the required packages. Normal calculations and exports use local files after installation. The app uses local fonts and browser assets.

The address 127.0.0.1 is your own computer. Do not change it to expose the server to others. The app has no login protection.

See [offline check limits](../07-testing-and-evidence/verification.md) and [safe use](../../SECURITY.md).

## Linux or macOS

Use Python 3.12 to create the environment and replace the Windows Python path with .venv/bin/python. For example:

~~~bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.lock
.venv/bin/python -m pip install -e . --no-deps
.venv/bin/python -m streamlit run app.py
~~~

The lock file comes from the tested Windows setup. Linux checks are configured in GitHub Actions, but no completed remote run is claimed. If a package is unavailable on your platform, report its name and error.

## Smaller Python-only installation

If you only need the calculation package, install with:

~~~powershell
.\.venv\Scripts\python -m pip install -e .
~~~

This needs NumPy and SciPy. The browser, study figures and development checks need extra packages. Use the main lock file for the full documented workflow.

## First check

Open the Axial bar example and follow [your first calculation](first-model.md). If setup fails, use [troubleshooting](../04-user-guide/troubleshooting.md).

## Read next

- [Your first bar calculation](first-model.md)

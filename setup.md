# Setup Guide

This guide walks you through setting up the **Supply Chain Control Tower Dashboard** project on a Windows machine.  Follow the steps below to configure your environment, install dependencies and run both the Excel and Streamlit dashboards.

## Prerequisites

Before you begin, ensure you have the following software installed:

- **Python 3.10+** – Download from [python.org](https://www.python.org/downloads/).  During installation, check the option to add Python to your system **PATH**.
- **Git** – Download and install Git from [git‑scm.com](https://git-scm.com/download/win).
- **Visual Studio Code (VS Code)** – Install from [code.visualstudio.com](https://code.visualstudio.com/) and add the Python extension.
- **Microsoft Excel** – Part of Microsoft 365 or Office 2016+ for the Excel dashboard.

## 1. Clone the Repository

Open a terminal (Command Prompt or Git Bash) and clone the repository from GitHub:

```bash
git clone https://github.com/your‑username/supply‑chain‑control‑tower‑dashboard.git
cd supply‑chain‑control‑tower‑dashboard/Supply_Chain_Control_Tower
```

Replace `your‑username` with your GitHub account name if necessary.

## 2. Verify Folder Structure

The `Supply_Chain_Control_Tower` folder should contain the following structure:

```
Supply_Chain_Control_Tower/
│
├── data/
│   ├── raw/        # place raw CSV or Excel datasets here
│   └── processed/  # processed data ready for analysis
│
├── excel_dashboard/  # Excel workbook(s) for the control tower
│
├── streamlit_app/
│   ├── app.py           # Streamlit dashboard script
│   └── requirements.txt # Python dependencies for the web app
│
├── scripts/       # Python or notebook scripts for data processing
├── reports/       # additional documentation, analysis or reports
├── screenshots/   # images for README and documentation
│
├── .gitignore
├── README.md
└── setup.md
```

## 3. Set Up a Python Virtual Environment

Creating a virtual environment isolates project dependencies and avoids conflicts.  Run the following commands inside the `Supply_Chain_Control_Tower` directory:

```bash
python -m venv venv

# Activate the environment
# On Windows Command Prompt
venv\Scripts\activate

# On PowerShell
venv\Scripts\Activate.ps1

# On Git Bash or WSL
source venv/Scripts/activate
```

Your command prompt should change to show `(venv)` indicating the environment is active.

## 4. Install Dependencies

With the virtual environment activated, install the required Python packages for the Streamlit app:

```bash
pip install -r streamlit_app/requirements.txt
```

You can add additional packages as needed by editing `streamlit_app/requirements.txt` and re‑running the command.

## 5. Run the Streamlit Dashboard

Start the web dashboard with the following commands:

```bash
cd streamlit_app
streamlit run app.py
```

Streamlit will launch a local web server and provide a URL (usually `http://localhost:8501`) that you can open in your browser to view the dashboard.

## 6. Work with the Excel Dashboard

Navigate to the `excel_dashboard` folder and open the Excel workbook using Microsoft Excel.  Use pivot tables, slicers and charts to explore the KPIs and interact with the data.  The workbook will be created as part of the project once data is available.

## 7. Data Processing

Store original datasets in the `data/raw` folder.  Use Python scripts or notebooks inside the `scripts` directory to clean and transform the raw data, then save the results to `data/processed`.  The dashboards should read from the processed files.

## Notes

- The `.gitignore` file excludes unnecessary files (temporary files, logs, virtual environments and large data directories) from version control.
- Use the `reports` directory to document analyses or business findings.
- Add screenshots of your dashboards to the `screenshots` folder to include them in the README.
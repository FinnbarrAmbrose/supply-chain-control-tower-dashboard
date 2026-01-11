# Supply Chain Control Tower Dashboard

## Project Overview

This project aims to build a **Supply Chain Control Tower Dashboard** that provides real‑time visibility into key logistics and supply chain metrics.  The dashboard will be implemented in two formats — an Excel dashboard for quick pivot‑table exploration and a Streamlit web application for an interactive, browser‑based experience.  Both dashboards will consume publicly available transportation and logistics data and present KPIs, charts and slicers that help analysts monitor performance, identify bottlenecks and make data‑driven decisions.

## Business Problem

Supply chain teams often struggle to gain end‑to‑end visibility across shipping routes, delivery performance and customer satisfaction.  Disparate data sources and manual reporting processes make it difficult to track on‑time delivery rates, compare routes or identify delays.  This project addresses that gap by creating a **control tower** – a centralised dashboard that aggregates raw logistics data into meaningful KPIs and visualisations.  The goal is to empower a supply chain administrator/analyst to monitor operations, flag issues early and drive continuous improvement.


## Business Context

This project represents a **Supply Chain Control Tower** for a mid-sized **consumer electronics distributor** operating a global supply network.

The company sources products from manufacturing plants across Asia and distributes into the UK and EU using a multimodal logistics network (sea, air, and road). The organisation works with global freight forwarders and operates a centralised warehouse and distribution model.

### Products
- Laptops  
- Smartphones  
- Tablets  
- Accessories  
- Networking equipment  

### Supply Network
- Manufacturing: China, Vietnam, Taiwan  
- Export Ports: Shanghai, Shenzhen, Ho Chi Minh  
- Import Ports: Rotterdam, Felixstowe, Hamburg  
- Distribution: UK & EU regional distribution centres  

### Business Objectives
- Maintain high on-time delivery performance (>98%)
- Control freight cost per order
- Identify high-risk lanes and carriers
- Detect operational exceptions early
- Protect margin and service levels

### Control Tower Purpose
The control tower provides:
- End-to-end shipment visibility
- Service performance monitoring (SLA)
- Operational risk detection
- Exception management
- Cost and margin exposure analysis
- Scenario-based decision support

---

### About the Dataset

The underlying dataset is a public logistics dataset containing coded identifiers (carrier codes, service codes, plant codes, customer IDs).

To make the dashboard interpretable in a portfolio and interview context, a **representative business narrative and label mappings** are applied (without altering the underlying metrics or calculations). This reflects standard industry practice for analytics demos and control tower prototypes.

## Key Performance Indicators (KPIs)

The dashboards will track and visualise a selection of important supply chain KPIs, such as:

- **On‑Time Delivery Rate:** percentage of deliveries that arrive by their scheduled time.
- **Average Delivery Time:** mean time taken to deliver goods between origin and destination.
- **Delivery Time Variance:** comparison of delivery times under different conditions (e.g. with vs. without congestion, across routes or customer ratings).
- **Customer Rating Distribution:** counts of customer satisfaction ratings across routes.
- **Delivery Count by Route and Rating:** number of deliveries broken down by route and rating categories.
- **Inventory Turnover and Stock Levels:** once inventory data is available, metrics describing how often stock is replenished.
- **Exception and Delay Counts:** counts of delayed shipments or exceptions.

These KPIs can be adjusted based on the specifics of the chosen dataset and business context.

## Dashboard Description

The project delivers two complementary dashboards:

1. **Excel Dashboard:**  An interactive Excel file using pivot tables, charts and slicers to explore KPIs.  It allows users to filter by date, route, rating and congestion status and provides quick summary statistics.  The Excel dashboard is useful for quick offline analysis and is accessible to non‑technical stakeholders.

2. **Streamlit Web App:**  A Python/Streamlit application that reads processed data and displays interactive charts in a web browser.  It will use pandas for data manipulation and Plotly or Altair for interactive visualisations.  The web app offers a richer user experience with custom filters, dynamic charts and the ability to deploy the dashboard on the web.

## Tech Stack

- **Excel** for the initial dashboard and data exploration.
- **Python** (with pandas and numpy) for data cleaning and transformation.
- **Streamlit** for building the web dashboard.
- **Plotly/Altair/Seaborn** for charts and visualisations.
- **VS Code** as the development environment.
- **Git & GitHub** for version control and collaboration.

## How to Run

Follow these steps to run the project on your local machine:

1. **Clone the repository** and navigate into the project directory:
   ```bash
   git clone https://github.com/your‑username/supply‑chain‑control‑tower‑dashboard.git
   cd supply‑chain‑control‑tower‑dashboard/Supply_Chain_Control_Tower
   ```
2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # Activate on Windows CMD
   venv\Scripts\activate
   # Or on PowerShell
   venv\Scripts\Activate.ps1
   ```
3. **Install dependencies**:
   ```bash
   pip install -r streamlit_app/requirements.txt
   ```
4. **Run the Streamlit app**:
   ```bash
   cd streamlit_app
   streamlit run app.py
   ```
5. **Explore the Excel dashboard**: open the files in the `excel_dashboard/` directory using Microsoft Excel and interact with pivot tables and charts.

## Screenshots

Place images of the Excel and Streamlit dashboards in the `screenshots/` folder as you build the project.  Embed them here to showcase the final product.
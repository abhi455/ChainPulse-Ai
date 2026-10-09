# ChainPulse AI

A full-stack supply-chain intelligence platform that helps teams centralize operational data, monitor product and supplier performance, forecast demand, evaluate risk, and test planning scenarios.

ChainPulse AI combines a Streamlit dashboard, FastAPI backend, SQLite database, and analytics services into one local application.

## What It Does

ChainPulse AI helps users answer practical supply-chain questions:

- Which products are driving demand and revenue?
- Is inventory below a safe reorder level?
- Which suppliers create reliability, quality, lead-time, or cost risk?
- Is demand variability being amplified through the supply chain?
- What could happen if demand, lead time, or inventory changes?
- Which operational actions should be prioritized?

## Core Features

### Dashboard

- Organization-level supply-chain overview
- Product-level demand, inventory, forecast, and performance summaries
- Central navigation for operations, analytics, and reporting

### Product Management

- Create and manage products by SKU
- Store category, unit cost, selling price, and lead-time data
- Browse product-level operational intelligence

### Demand Management

- Add demand records by product and date
- Track quantities and revenue
- Visualize historical demand patterns
- Use demand history as input for forecasting

### Inventory Intelligence

- Store inventory snapshots by product and date
- Calculate safety stock
- Calculate reorder points
- Calculate economic order quantity (EOQ)
- Calculate days of inventory coverage
- Identify inventory risk conditions

### Supplier Intelligence

- Store supplier records by organization
- Evaluate supplier reliability, quality, lead time, and cost
- Produce an overall supplier score and risk level
- Generate improvement recommendations

### Bullwhip Effect Analysis

- Compare customer demand with retailer, distributor, and manufacturer orders
- Calculate variability at each supply-chain level
- Calculate bullwhip ratios and overall severity
- Show recommendations based on amplification risk
- Support Bullwhip data import through Connect Data

### Connect Data and Ingestion

- Create connections for CSV, Excel, JSON, SQLite, SQL, and REST API sources
- Preview connected data before importing
- Detect columns automatically through `AutoMapper`
- Review and edit column mappings
- Validate records before writing to the database
- Import validated data into Products, Demand, Inventory, or Bullwhip records
- Display import results and row-level errors

### Forecasting

- Generate moving-average forecasts
- Generate exponential-smoothing forecasts
- Use real demand history stored for a selected product
- Compare forecasting model outputs in the dashboard

### Risk and Decisions

- Evaluate combined demand, inventory, supplier, and Bullwhip risk
- Identify primary operational risk drivers
- Generate recommended actions with priority and confidence levels

### Scenario Simulations

- Simulate changes in demand, lead time, and inventory
- Compare baseline inventory metrics with scenario outcomes
- Save simulation scenarios and completed runs to the database

### Authentication and Organizations

- User registration, onboarding, and login
- Organization-scoped data access
- JWT-based authentication
- Role-aware product creation and protected API routes

## Technology Stack

| Area | Technology |
|---|---|
| Frontend | Streamlit |
| Backend API | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Migrations | Alembic |
| Validation | Pydantic |
| Data Processing | Pandas, OpenPyXL |
| Server | Uvicorn |
| Authentication | JWT, bcrypt, python-jose |
| Forecasting | Moving Average, Exponential Smoothing |

## Architecture

```text
Streamlit Dashboard
        ↓
FastAPI API Routes
        ↓
Services / Analytics / Ingestion
        ↓
SQLAlchemy Models and Repositories
        ↓
SQLite Database
```

## Local Setup

```powershell
git clone https://github.com/abhi455/ChainPulse-Ai.git
cd ChainPulse-Ai

py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python start_chainpulse.py
```

Open the dashboard:

```text
http://localhost:8501
```

Open the FastAPI documentation:

```text
http://localhost:8000/docs
```

## Validation

```powershell
.\.venv\Scripts\python.exe -m compileall -q backend frontend config core integrations
.\.venv\Scripts\python.exe -c "import backend.main; print('Backend import passed')"
```

## Project Structure

```text
backend/       FastAPI routes, services, database models, ingestion, analytics
frontend/      Streamlit dashboard and user interface
config/        Application configuration
core/          Supply-chain calculation and simulation components
data/          Local runtime database and data directories
storage/       Runtime imports, exports, and uploads
tests/         Test structure for unit, API, integration, and end-to-end tests
```

## Security

The repository excludes secrets, local databases, user uploads, logs, and virtual environments. Create local environment variables from the example configuration files when needed.

## Portfolio Note

ChainPulse AI is a portfolio project demonstrating full-stack Python development, data ingestion, API design, database-backed analytics, forecasting, supply-chain decision support, and interactive dashboard design.

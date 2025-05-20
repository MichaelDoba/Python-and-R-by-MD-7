# 🏥 Healthcare Spending Survey Tool
A full-stack web application developed by Michael Doba designed to collect, store, and analyze household income and expense data to support product development in the healthcare sector.


## 📌 Project Purpose
This tool supports data-driven decision-making for a healthcare product launch. It gathers essential participant information such as age, gender, income, and categorized expenses. The insights derived help identify spending patterns across demographics.


## 🧠 What the Code Does
#### 1.App.py
Core Application Logic
#### 2.Flask Web App:
Provides a front-end survey form to collect data.
#### 3.MongoDB Integration: 
Attempts to store submissions in a remote MongoDB database.
#### 4.CSV Logging: 
Every submission is also appended to a local survey_data.csv file for offline access and redundancy.
#### 5.Visualization Generation:
    Boxplot: Income distribution by age group and gender.

    Bar Chart: Spending by category and gender.

    Pie Chart: Overall breakdown of expense categories.
#### 6.Flask Routes:

    / → Survey form

    /thank-you → Confirmation page

    /analyze → View auto-generated charts

    /export-csv → Download the full dataset
#### 7.charts.ipynb
Data Analysis Notebook
#### 8.Reads survey_data.csv
#### 9.Performs custom analysis and generates charts for client reports and presentations


## 🔄 Data Flow Summary

#### 1.User submits survey via web form.

#### 2.Data is:

    Stored in MongoDB (if available)

    Logged in survey_data.csv

#### 3.Visualization logic reads the CSV file and outputs charts to /static/visualizations/.

#### 4.Visuals are embedded into the /analyze route for quick review.


## ▶️ How to Run Locally
#### Install dependencies:

    pip install -r requirements.txt
    
#### Run the app:

    python App.py
    
#### Access the survey:

Open your browser and go to http://127.0.0.1:5000


## 📁 Folder Structure

    project/

    ├── app.py                  # Main backend logic

    ├── data/

    │   └── survey_data.csv     # Collected survey data

    ├── static/

    │   └── visualizations/     # Generated charts (.png)

    ├── templates/

    │   ├── survey.html         # Form UI

    │   ├── thank_you.html      # Post-submit screen

    │   └── analysis.html       # Visualization display

    ├── charts.ipynb            # Optional deep-dive notebook

    ├── requirements.txt        # Python dependencies

    └── README.md               # Project documentation


## 🧾 Key Functional Highlights

#### 1.Designed for easy AWS deployment

#### 2.Lightweight and extendable

#### 3.Clean separation of concerns: data capture, storage, visualization

#### 4.Visualization outputs ready for export into PowerPoint or client reports

#### 5.Jupyter-friendly CSV format for external data analysis


## 📊 Insights???

This application makes it simple to gather participant data, process it efficiently, and deliver clean, client-ready visualizations. Whether used internally for strategy or externally for presentations, the outputs help highlight spending trends across demographics—especially valuable in healthcare-related market planning.




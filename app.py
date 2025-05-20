import os
import csv
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from pymongo import MongoClient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from dotenv import load_dotenv

# Loading environment variables
load_dotenv()

# App Configurations
app = Flask(__name__, static_folder='static')
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
VIS_DIR = os.path.join(BASE_DIR, 'static', 'visualizations')
DATA_DIR = os.path.join(BASE_DIR, 'data')
CSV_FILE_PATH = os.path.join(DATA_DIR, 'survey_data.csv')

os.makedirs(VIS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

CSV_HEADERS = [
    'age', 'gender', 'total_income', 'utilities', 'entertainment',
    'healthcare', 'education', 'shopping', 'timestamp'
]

# MongoDB Data Manager
class DataManager:
    def __init__(self):
        self.using_mongodb = False
        self.local_storage = []
        self._connect_to_mongodb()

    def _connect_to_mongodb(self):
        uri = "mongodb+srv://michaeldoba:Nexfordproject@cluster0.v3uw5dq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        if not uri:
            print("ℹ️ MONGODB_URI not set - using local storage")
            return
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command('ping')
            self.db = self.client['healthcare_survey']
            self.collection = self.db['responses']
            self.using_mongodb = True
            print("✅ Connected to MongoDB Atlas")
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            self.using_mongodb = False

    def save_data(self, data):
        if self.using_mongodb:
            try:
                result = self.collection.insert_one(data)
                data['_id'] = str(result.inserted_id)
                return True, "database"
            except Exception as e:
                print(f"⚠️ MongoDB save failed: {e}")
        self.local_storage.append(data)
        return True, "local storage"

    def get_all_data(self):
        if self.using_mongodb:
            try:
                return list(self.collection.find({}, {'_id': 0}))
            except Exception as e:
                print(f"⚠️ MongoDB read failed: {e}")
        return self.local_storage

data_manager = DataManager()

def append_to_csv(data):
    write_header = not os.path.exists(CSV_FILE_PATH) or os.path.getsize(CSV_FILE_PATH) == 0
    try:
        with open(CSV_FILE_PATH, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if write_header:
                writer.writeheader()
            writer.writerow({k: data.get(k, 0) for k in CSV_HEADERS})
        return True
    except Exception as e:
        print(f"❌ CSV append failed: {e}")
        return False

def generate_visualizations():
    if not os.path.exists(CSV_FILE_PATH):
        print(f"❌ Data file not found at {CSV_FILE_PATH}")
        return False

    try:
        df = pd.read_csv(CSV_FILE_PATH)
    except pd.errors.ParserError as e:
        print(f"❌ CSV parsing error: {e}")
        return False

    column_map = {
        'age': ['age'], 'gender': ['gender'], 'total_income': ['total_income', 'income'],
        'utilities': ['utilities'], 'entertainment': ['entertainment'],
        'healthcare': ['healthcare', 'medical'], 'education': ['education'],
        'shopping': ['shopping']
    }

    data = pd.DataFrame({
        k: df[next((col for col in v if col in df.columns), None)] if any(col in df.columns for col in v) else 0
        for k, v in column_map.items()
    })

    # Visualisation 1 : Income by Age Group (Jupyter Code inclusion for real time visual updates)
    plt.figure(figsize=(12, 6))
    bins = [0, 18, 25, 35, 50, 65, 100]
    labels = ['<18', '18-24', '25-34', '35-49', '50-64', '65+']
    data['age_group'] = pd.cut(data['age'], bins=bins, labels=labels)
    sns.boxplot(data=data, x='age_group', y='total_income', hue='gender', showfliers=False)
    plt.title('Income Distribution by Age Group')
    plt.savefig(os.path.join(VIS_DIR, 'income_by_age.png'), bbox_inches='tight')
    plt.close()

    # Visualisation 2 : Spending by Category and Gender (Jupyter Code inclusion for real time visual updates)
    plt.figure(figsize=(12, 6))
    spending_cols = ['utilities', 'entertainment', 'education', 'healthcare', 'shopping']
    data.groupby('gender')[spending_cols].sum().plot(kind='bar', stacked=True)
    plt.title('Spending by Category and Gender')
    plt.savefig(os.path.join(VIS_DIR, 'spending_by_gender.png'), bbox_inches='tight')
    plt.close()

    # Visualisation 3 : Spending Pie Chart (Jupyter Code inclusion for real time visual updates)
    plt.figure(figsize=(8, 8))
    data[spending_cols].sum().plot.pie(autopct='%1.1f%%', labels=spending_cols)
    plt.title('Overall Spending Distribution')
    plt.ylabel('')
    plt.savefig(os.path.join(VIS_DIR, 'spending_pie.png'), bbox_inches='tight')
    plt.close()

    return True

# Survey form
@app.route('/', methods=['GET', 'POST'])
def survey():
    if request.method == 'POST':
        try:
            form = request.form
            survey_data = {
                'age': int(form['age']),
                'gender': form['gender'],
                'total_income': float(form['total_income']),
                'utilities': float(form.get('utilities', 0)),
                'entertainment': float(form.get('entertainment', 0)),
                'healthcare': float(form.get('healthcare', 0)),
                'education': float(form.get('education', 0)),
                'shopping': float(form.get('shopping', 0)),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

            success, storage = data_manager.save_data(survey_data)
            if not append_to_csv(survey_data):
                raise Exception("Failed to save to CSV")

            flash(f"Data saved to {storage}", 'success')
            return redirect(url_for('thank_you'))
        except Exception as e:
            flash(f"Error: {e}", 'error')
            return redirect(url_for('survey'))

    return render_template('survey.html')

# Thank_you form
@app.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

# Analyse form
@app.route('/analyze')
def analyze():
    if not generate_visualizations():
        flash("Could not generate visualizations", 'error')
        return redirect(url_for('survey'))

    charts = {
        'income_chart': 'income_by_age.png',
        'spending_chart': 'spending_by_gender.png',
        'pie_chart': 'spending_pie.png'
    }

    return render_template('analysis.html', **{
        k: url_for('static', filename=f'visualizations/{v}') for k, v in charts.items()
    })

# Export CSV File
@app.route('/export-csv')
def export_csv():
    if os.path.exists(CSV_FILE_PATH):
        return send_from_directory(DATA_DIR, 'survey_data.csv', as_attachment=True)
    flash("CSV file not found", 'error')
    return redirect(url_for('survey'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

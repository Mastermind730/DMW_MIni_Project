from flask import Flask, render_template, send_file
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Load data
df = pd.read_csv("Finance_data.csv")

# Data preprocessing
df.drop(['Mutual_Funds', 'Equity_Market', 'Debentures', 'Government_Bonds', 
         'Fixed_Deposits', 'PPF', 'Gold'], axis=1, inplace=True)

def plot_to_image(plt):
    """Converts a Matplotlib plot to an image."""
    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return plot_url

@app.route('/')
def index():
    sns.set_style('darkgrid')

    # Gender distribution plot
    plt.figure(figsize=(10, 6))
    sns.countplot(df['gender'], linewidth=3, palette="Set2", edgecolor='black')
    gender_plot = plot_to_image(plt)

    # Age distribution plot
    plt.figure(figsize=(10, 6))
    sns.countplot(x='age', data=df, palette="Set3", linewidth=2, edgecolor='black')
    age_plot = plot_to_image(plt)

    # Factors affecting investment
    plt.figure(figsize=(10, 6))
    sns.countplot(x=df['Factor'], palette='coolwarm', linewidth=2, edgecolor='black')
    factor_plot = plot_to_image(plt)

    # Gender vs Investment factors
    plt.figure(figsize=(10, 6))
    sns.countplot(x=df['gender'], hue=df['Factor'], palette='Oranges', linewidth=2, edgecolor='black')
    gender_factor_plot = plot_to_image(plt)

    return render_template('index.html', 
                           gender_plot=gender_plot, 
                           age_plot=age_plot, 
                           factor_plot=factor_plot, 
                           gender_factor_plot=gender_factor_plot)

if __name__ == '__main__':
    app.run(debug=True)

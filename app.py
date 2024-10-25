from flask import Flask, render_template, send_file
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sklearn.cluster import KMeans
import os

app = Flask(__name__)

# Load dataset (assuming dataset is in the same directory)
df = pd.read_csv("cars_ds_final.csv")

# Function to get the total number of cars
def get_total_cars():
    return len(df)

# Function to get the most common fuel type
def get_most_common_fuel():
    return df['Fuel_Type'].mode()[0]

# Home route
@app.route('/')
def home():
    total_cars = get_total_cars()
    most_common_fuel = get_most_common_fuel()
    
    # Pass the values to the template
    return render_template('home.html', total_cars=total_cars, most_common_fuel=most_common_fuel)
@app.route('/car_makers_pie')
def car_makers_pie():
    plt.figure(figsize=(10, 20))
    ax = plt.gca()
    df['Make'].value_counts().plot(ax=ax, kind='pie', autopct='%1.1f%%', startangle=90)
    plt.title('Top Car Making Companies in India')
    pie_chart_path = "static/images/pie_chart.png"
    plt.savefig(pie_chart_path)
    plt.close()
    return render_template('pie_chart.html', pie_chart_path=pie_chart_path)
# Route to show dataset summary
@app.route('/summary')
def summary():
    description = df.describe().to_html(classes='table table-striped table-bordered')
    return render_template('summary.html', description=description)

# Route to show missing values
@app.route('/missing')
def missing():
    missing_values = df.isnull().sum().to_frame().to_html(classes='table table-striped table-bordered')
    return render_template('missing_values.html', missing_values=missing_values)

# Route for KMeans Clustering
@app.route('/kmeans')
def kmeans_clustering():
    # Select relevant numeric columns for clustering
    # Height	Length	Width

    numeric_columns = ['Cylinders', 'Valves_Per_Cylinder', 'Gears']  # You can adjust these based on your dataset
    df_numeric = df[numeric_columns].dropna()

    # Apply KMeans
    kmeans = KMeans(n_clusters=3)
    df_numeric['Cluster'] = kmeans.fit_predict(df_numeric)

    # Create an interactive scatter plot using Plotly
    fig = px.scatter(df_numeric, x='Cylinders', y='Valves_Per_Cylinder', color='Cluster', size='Valves_Per_Cylinder',
                     title="KMeans Clustering on Cars Dataset")
    scatter_path = "static/images/kmeans_scatter.html"
    fig.write_html(scatter_path)

    return render_template('kmeans_clustering.html', scatter_path=scatter_path)

# Route to display the correlation matrix
@app.route('/correlation_matrix')
def correlation_matrix():
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(), annot=True, cmap="coolwarm", fmt='.2f', linewidths=0.5)
    plt.title('Correlation Matrix', fontsize=18)
    correlation_matrix_path = "static/images/correlation_matrix.png"
    plt.savefig(correlation_matrix_path)
    plt.close()
    return render_template('correlation_matrix.html', correlation_matrix_path=correlation_matrix_path)

# Route to display box plot for numeric columns
@app.route('/box_plot')
def box_plot():
    numeric_columns_to_visualize = ['numeric_column_1', 'numeric_column_2']
    df_numeric = pd.DataFrame({
        'numeric_column_1': [5, 10, 15, 20, 25, 30, 35, 40, 45],
        'numeric_column_2': [100, 150, 200, 250, 300, 350, 400, 450, 500]
    })
    sns.set_palette("husl")
    plt.figure(figsize=(12, 8))
    sns.boxplot(data=df_numeric[numeric_columns_to_visualize], orient='h', width=0.9)
    plt.title('Box Plots of Numeric Variables', fontsize=24)
    box_plot_path = "static/box_plot.png"
    plt.savefig(box_plot_path)
    plt.close()
    return render_template('box_plot.html', box_plot_path=box_plot_path)

# Route to display categorical bar chart
@app.route('/categorical_bar_chart')
def categorical_bar_chart():
    df_categorical = pd.DataFrame({
        'column_1': ['Category_A', 'Category_B', 'Category_A', 'Category_A', 'Category_B'],
        'column_2': ['Type_X', 'Type_Y', 'Type_X', 'Type_Y', 'Type_X'],
    })
    counts = df_categorical.apply(pd.value_counts)
    plt.figure(figsize=(18, 10))
    counts.T.plot(kind='bar', stacked=True, colormap='magma')
    plt.title('Categorical Variables', fontsize=30)
    plt.xlabel('Category')
    plt.ylabel('Count')
    bar_chart_path = "static/bar_chart.png"
    plt.savefig(bar_chart_path)
    plt.close()
    return render_template('categorical_bar_chart.html', bar_chart_path=bar_chart_path)

if __name__ == "__main__":
    app.run(debug=True)

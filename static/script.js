document.addEventListener("DOMContentLoaded", function () {
    // Fetch and render pie chart for car makes
    fetch("/api/make_distribution")
        .then(response => response.json())
        .then(data => {
            Plotly.newPlot('pie-chart', data.data, data.layout);
        });

    // Fetch and display the body type count plot image
    fetch('/api/body_type_plot')
        .then(response => response.json())
        .then(data => {
            document.getElementById('body-type-image').src = 'data:image/png;base64,' + data.image;
        });
});

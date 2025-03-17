document.addEventListener("DOMContentLoaded", function () {
    updateCharts();
});

function updateCharts() {
    let year = document.getElementById("year-filter").value;
    let crimeType = document.getElementById("type-filter").value;

    fetch(`/bar_chart_data?year=${year}&type=${crimeType}`)
        .then(response => response.json())
        .then(data => {
            let fig = {
                x: data.map(row => row.garda_region),
                y: data.map(row => row.value),
                type: "bar",
            };
            Plotly.newPlot("bar-chart", [fig]);
        });

    fetch(`/crime_pie_chart`)
        .then(response => response.json())
        .then(data => {
            let fig = JSON.parse(data);
            Plotly.newPlot("pie-chart", fig.data, fig.layout);
        });
}
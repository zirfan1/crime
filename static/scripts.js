document.addEventListener("DOMContentLoaded", function () {
    updateCharts();
});

function updateCharts() {
    let year = document.getElementById("year-filter").value;
    let crimeType = document.getElementById("type-filter").value;

    let url = `/bar_chart_data`;
    let params = [];
    if (year) params.push(`year=${year}`);
    if (crimeType && crimeType !== 'All Types') params.push(`type=${crimeType}`);
    if (params.length) url += `?${params.join('&')}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            let fig = {
                x: data.map(row => row.garda_region),
                y: data.map(row => row.value),
                type: "bar",
                marker: { color: "blue" }
            };
            Plotly.newPlot("bar-chart", [fig], { title: "Crime Count by Garda Region" });
        });

    // Updating pie chart only if necessary or upon initial load
    if (!year && !crimeType) {
        fetch(`/crime_pie_chart`)
            .then(response => response.json())
            .then(data => {
                let fig = JSON.parse(data);
                Plotly.newPlot("pie-chart", fig.data, fig.layout);
            });
    }
}

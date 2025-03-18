document.addEventListener("DOMContentLoaded", function () {
    updateCharts(); // Call to update the charts on initial load
});

function updateCharts() {
    let year = document.getElementById("year-filter").value;
    let crimeType = document.getElementById("type-filter").value;

    let url = `/bar_chart_data`; // Base URL for fetching bar chart data
    let params = []; // Initialize parameters array
    if (year) params.push(`year=${year}`); // Add year to params if set
    if (crimeType && crimeType !== 'All Types') params.push(`type=${crimeType}`); // Add crime type to params if set and not default
    if (params.length) url += `?${params.join('&')}`; // Append params to URL if any

    // Fetch and display the bar chart data
    fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log("Bar Chart Data:", data); // Log bar chart data for debugging
            let fig = {
                x: data.map(row => row.garda_region),
                y: data.map(row => row.value),
                type: "bar",
                marker: { color: "blue" }
            };
            Plotly.newPlot("bar-chart", [fig], { title: "Crime Count by Garda Region" });
        });

    // Fetch and update the line graph every time, regardless of filters
    fetch(`/line_chart_data?year=${year}&type=${crimeType}`) // Assuming this endpoint exists
        .then(response => response.json())
        .then(data => {
            console.log("Line Graph Data:", data); // Log line graph data for debugging
            let layout = {
                title: 'Crime Trends Over Time',
                xaxis: {
                    title: 'Year'
                },
                yaxis: {
                    title: 'Number of Incidents'
                }
            };
            let trace = {
                x: data.map(item => item.year),
                y: data.map(item => item.value),
                type: 'line',
                marker: { color: 'red' }
            };
            Plotly.newPlot("line-chart", [trace], layout);
        })
        .catch(error => {
            console.error('Error fetching line graph data:', error);
        });
}

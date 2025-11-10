# Performance Benchmarks

This page displays performance benchmark results for the bluetooth-sig-python library.

## Historical Trends

<div id="benchmark-trends">
<p>Loading historical benchmark data...</p>
</div>

## Latest Results

<div id="benchmark-results">
<p>Loading benchmark results...</p>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<script>
// Load historical trends
fetch('./history.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Historical data not available yet');
    }
    return response.json();
  })
  .then(history => {
    const container = document.getElementById('benchmark-trends');

    if (!history || history.length === 0) {
      container.innerHTML = '<p><em>Historical trends will appear after multiple benchmark runs.</em></p>';
      return;
    }

    // Get unique benchmark names
    const benchmarkNames = new Set();
    history.forEach(entry => {
      Object.keys(entry.results || {}).forEach(name => benchmarkNames.add(name));
    });

    // Create a canvas for each benchmark
    let html = '<div class="charts-container">';

    Array.from(benchmarkNames).sort().forEach(benchName => {
      html += `<div class="chart-wrapper">`;
      html += `<h3>${benchName}</h3>`;
      html += `<canvas id="chart-${benchName.replace(/[^a-zA-Z0-9]/g, '_')}"></canvas>`;
      html += `</div>`;
    });

    html += '</div>';
    container.innerHTML = html;

    // Render charts
    Array.from(benchmarkNames).sort().forEach(benchName => {
      const canvasId = `chart-${benchName.replace(/[^a-zA-Z0-9]/g, '_')}`;
      const canvas = document.getElementById(canvasId);

      const labels = history.map(entry => {
        const date = new Date(entry.timestamp);
        return date.toLocaleDateString('en-GB', { month: 'short', day: 'numeric' });
      });

      const means = history.map(entry => entry.results[benchName]?.mean || null);
      const stddevs = history.map(entry => entry.results[benchName]?.stddev || null);

      new Chart(canvas, {
        type: 'line',
        data: {
          labels: labels,
          datasets: [{
            label: 'Mean (µs)',
            data: means,
            borderColor: 'rgb(75, 192, 192)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            tension: 0.1,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            title: {
              display: false
            },
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              title: {
                display: true,
                text: 'Time (µs)'
              }
            },
            x: {
              title: {
                display: true,
                text: 'Date'
              }
            }
          }
        }
      });
    });
  })
  .catch(error => {
    const container = document.getElementById('benchmark-trends');
    container.innerHTML = `
      <div class="admonition note">
        <p class="admonition-title">Note</p>
        <p>Historical trends will appear after the first benchmark run on the main branch.</p>
      </div>
    `;
  });
// Load and display benchmark results from JSON
fetch('./benchmark.json')
  .then(response => {
    if (!response.ok) {
      throw new Error('Benchmark data not available');
    }
    return response.json();
  })
  .then(data => {
    const container = document.getElementById('benchmark-results');

    if (!data.benchmarks || data.benchmarks.length === 0) {
      container.innerHTML = '<p>No benchmark data available yet.</p>';
      return;
    }

    // Create a table
    let html = '<table><thead><tr>';
    html += '<th>Benchmark</th>';
    html += '<th>Min (µs)</th>';
    html += '<th>Max (µs)</th>';
    html += '<th>Mean (µs)</th>';
    html += '<th>StdDev</th>';
    html += '<th>Rounds</th>';
    html += '</tr></thead><tbody>';

    data.benchmarks.forEach(bench => {
      const stats = bench.stats;
      html += '<tr>';
      html += `<td><code>${bench.name}</code></td>`;
      html += `<td>${(stats.min * 1000000).toFixed(2)}</td>`;
      html += `<td>${(stats.max * 1000000).toFixed(2)}</td>`;
      html += `<td>${(stats.mean * 1000000).toFixed(2)}</td>`;
      html += `<td>${(stats.stddev * 1000000).toFixed(2)}</td>`;
      html += `<td>${stats.rounds}</td>`;
      html += '</tr>';
    });

    html += '</tbody></table>';

    // Add metadata
    html += '<div class="benchmark-metadata">';
    html += `<p><strong>Generated:</strong> ${data.datetime || 'Unknown'}</p>`;
    html += `<p><strong>Machine:</strong> ${data.machine_info?.node || 'GitHub Actions'}</p>`;
    html += `<p><strong>Python:</strong> ${data.machine_info?.python_version || 'Unknown'}</p>`;
    html += '</div>';

    container.innerHTML = html;
  })
  .catch(error => {
    const container = document.getElementById('benchmark-results');
    container.innerHTML = `
      <div class="admonition note">
        <p class="admonition-title">Note</p>
        <p>Benchmark results will appear here after the first successful benchmark run on the main branch.</p>
        <p>${error.message}</p>
      </div>
    `;
  });
</script>

<style>
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2em;
  margin: 2em 0;
}

.chart-wrapper {
  background: #fff;
  padding: 1em;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chart-wrapper h3 {
  margin-top: 0;
  font-size: 0.9em;
  color: #333;
  font-family: monospace;
}

.chart-wrapper canvas {
  height: 250px !important;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1em 0;
}

th, td {
  padding: 0.5em;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

th {
  background-color: #f4f4f4;
  font-weight: bold;
}

tr:hover {
  background-color: #f9f9f9;
}

.benchmark-metadata {
  margin-top: 2em;
  padding: 1em;
  background-color: #f4f4f4;
  border-radius: 4px;
}

.benchmark-metadata p {
  margin: 0.25em 0;
}
</style>

## About These Benchmarks

These benchmarks measure the performance of key operations in the bluetooth-sig-python library:

- **Characteristic decoding**: Time to parse and decode characteristic values
- **UUID resolution**: Time to resolve UUIDs to names using the registry
- **Data type parsing**: Time to parse common Bluetooth data types

Benchmarks are run automatically on every push to the main branch using pytest-benchmark. Results from pull requests are compared against the main branch baseline, and alerts are raised if performance regresses by more than 200%.

For the complete benchmark suite and methodology, see the [tests/benchmarks/](https://github.com/ronan/bluetooth-sig-python/tree/main/tests/benchmarks) directory.

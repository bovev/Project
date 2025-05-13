let revenueChart;
let occupancyChart;

// Set default font family and other Chart.js settings
function setChartDefaults() {
  Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";
  Chart.defaults.responsive = true;
  Chart.defaults.maintainAspectRatio = false;
}

document.addEventListener('DOMContentLoaded', function() {
  try {
    setChartDefaults();
    
    // Get any filter values from the form
    const formElement = document.querySelector('.filter-form');
    let queryParams = '';
    
    if (formElement) {
      const formData = new FormData(formElement);
      const params = new URLSearchParams();
      
      for (const [key, value] of formData) {
        if (value) {
          params.append(key, value);
        }
      }
      
      queryParams = params.toString();
      if (queryParams) {
        queryParams = '?' + queryParams;
      }
    }
    
    // Show loading state
    document.querySelectorAll('.chart-container').forEach(container => {
      const loadingElement = container.querySelector('.chart-loading');
      const canvasElement = container.querySelector('canvas');
      
      if (loadingElement) loadingElement.style.display = 'block';
      if (canvasElement) canvasElement.style.display = 'none';
    });
    
    // Fetch data from API
    fetch(`/reporting/api/data${queryParams}`)
      .then(response => {
        if (!response.ok) {
          throw new Error(`Network response was not ok: ${response.status}`);
        }
        return response.json();
      })
      .then(reportData => {
        console.log("Report data received:", reportData);
        
        // Hide loaders, show canvases - UPDATED CODE
        document.querySelectorAll('.chart-container').forEach(container => {
          const loadingElement = container.querySelector('.chart-loading');
          const canvasElement = container.querySelector('canvas');
          
          if (loadingElement) loadingElement.style.display = 'none';
          if (canvasElement) canvasElement.style.display = 'block';
        });
        
        // Update stats
        const totalRevenueEl = document.querySelector('.card-revenue .stat-value');
        if (totalRevenueEl) {
          totalRevenueEl.textContent = `€${reportData.stats.total_revenue.toFixed(2)}`;
        }
        
        // Process data
        const months = reportData.months;
        const revenueData = reportData.revenue;
        const cottageOccupancy = reportData.occupancy;
        const translations = reportData.translations;
        
        // Calculate and display average occupancy
        let totalOccupancy = 0;
        let totalPoints = 0;
        cottageOccupancy.forEach(cottage => {
          cottage.data.forEach(value => {
            totalOccupancy += value;
            totalPoints++;
          });
        });
        
        const avgOccupancy = totalPoints > 0 ? (totalOccupancy / totalPoints).toFixed(1) : "0.0";
        const avgElement = document.getElementById('avgOccupancy');
        if (avgElement) {
          avgElement.textContent = avgOccupancy;
        }
        
        // Revenue Chart
        const revenueElement = document.getElementById('revenueChart');
        if (revenueElement) {
          const ctxRevenue = revenueElement.getContext('2d');
          // Destroy previous chart instance if it exists
          if (revenueChart) {
            revenueChart.destroy();
          }
          // Create new chart instance - FIX: Store the chart instance
          revenueChart = new Chart(ctxRevenue, {
            type: 'bar',
            data: {
              labels: months,
              datasets: [{
                label: translations.monthlyRevenue,
                data: revenueData,
                backgroundColor: 'rgba(78, 115, 223, 0.5)',
                borderColor: 'rgba(78, 115, 223, 1)',
                borderWidth: 1
              }]
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    callback: function(value) {
                      return '€' + value;
                    }
                  }
                }
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return translations.revenue + ': €' + context.raw.toFixed(2);
                    }
                  }
                }
              }
            }
          });
        }
        
        // Occupancy Chart
        const occupancyElement = document.getElementById('occupancyChart');
        if (occupancyElement) {
          const ctxOccupancy = occupancyElement.getContext('2d');
          // Destroy previous chart instance if it exists
          if (occupancyChart) {
            occupancyChart.destroy();
          }
          // Create new chart instance - FIX: Store the chart instance
          occupancyChart = new Chart(ctxOccupancy, {
            type: 'line',
            data: {
              labels: months,
              datasets: cottageOccupancy.map(cottage => {
                return {
                  label: cottage.name,
                  data: cottage.data,
                  borderColor: cottage.color || '#4e73df',
                  backgroundColor: (cottage.color || '#4e73df').replace('rgb', 'rgba').replace(')', ', 0.1)'),
                  borderWidth: 2,
                  tension: 0.1
                };
              })
            },
            options: {
              responsive: true,
              maintainAspectRatio: false,
              scales: {
                y: {
                  beginAtZero: true,
                  max: 100,
                  ticks: {
                    callback: function(value) {
                      return value + '%';
                    }
                  }
                }
              },
              plugins: {
                tooltip: {
                  callbacks: {
                    label: function(context) {
                      return context.dataset.label + ': ' + context.raw + '%';
                    }
                  }
                }
              }
            }
          });
        }
      })
      .catch(error => {
        // FIX: Improved error handling that doesn't destroy canvas elements
        console.error('Error fetching report data:', error);
        document.querySelectorAll('.chart-container').forEach(container => {
          const loadingElement = container.querySelector('.chart-loading');
          const canvasElement = container.querySelector('canvas');
          
          if (loadingElement) {
            loadingElement.innerHTML = '<div class="alert alert-danger">Error loading chart data.</div>';
            loadingElement.style.display = 'block';
          }
          
          if (canvasElement) {
            canvasElement.style.display = 'none';
          }
        });
      });
    
    // Print functionality
    const printButton = document.getElementById('print-report');
    if (printButton) {
      printButton.addEventListener('click', function() {
        window.print();
      });
    }
  } catch (error) {
    console.error("Error in charts.js:", error);
  }
});



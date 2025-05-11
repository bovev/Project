document.addEventListener('DOMContentLoaded', function() {
  try {
    console.log("Chart.js script loaded");
    
    // Check if reportData exists
    if (!window.reportData) {
      console.error("window.reportData is undefined!");
      return;
    }
    
    // Log the data we're working with
    console.log("Report data:", window.reportData);
    
    // Get data from the window object (will be set in the HTML)
    const months = window.reportData.months;
    const revenueData = window.reportData.revenue;
    const cottageOccupancy = window.reportData.occupancy;
    const translations = window.reportData.translations;
    
    // Calculate average occupancy
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
    if (!avgElement) {
      console.error("Element with ID 'avgOccupancy' not found!");
    } else {
      avgElement.textContent = avgOccupancy;
    }
    
    // Revenue Chart
    const revenueElement = document.getElementById('revenueChart');
    if (!revenueElement) {
      console.error("Element with ID 'revenueChart' not found!");
    } else {
      const ctxRevenue = revenueElement.getContext('2d');
      new Chart(ctxRevenue, {
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
    if (!occupancyElement) {
      console.error("Element with ID 'occupancyChart' not found!");
    } else {
      const ctxOccupancy = occupancyElement.getContext('2d');
      new Chart(ctxOccupancy, {
        type: 'line',
        data: {
          labels: months,
          datasets: cottageOccupancy.map(cottage => {
            return {
              label: cottage.name,
              data: cottage.data,
              borderColor: cottage.color || '#4e73df', // Provide default color if missing
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
    
    // Print functionality
    const printButton = document.getElementById('print-report');
    if (!printButton) {
      console.error("Element with ID 'print-report' not found!");
    } else {
      printButton.addEventListener('click', function() {
        window.print();
      });
    }
  } catch (error) {
    console.error("Error in charts.js:", error);
  }
});
function plot_deal_closed_report_price_bar_graph(elemId, labels, data_won, data_lost) {
    var ctx = document.getElementById(elemId).getContext('2d');
    var myChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: '# Deals Won by Users (USD)',
                                data: data_won,
                                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                                borderColor: 'rgba(54, 162, 235, 0.85)',
                                borderWidth: 1
                            }, {
                                label: '# Deals Lost by Users (USD)',
                                data: data_lost,
                                backgroundColor: 'rgba(243, 99, 113, 0.5)',
                                borderColor: 'rgba(243, 99, 113, 0.5)',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            layout: {
                               padding: {
                                  right: 12
                               }
                            },
                            scales: {
                                yAxes: [
                                    {
                                        ticks: {
                                            beginAtZero: true,
                                            callback: function(value) {
                                                 var ranges = [
                                                    { divider: 1e6, suffix: 'M' },
                                                    { divider: 1e3, suffix: 'k' }
                                                 ];
                                                 function formatNumber(n) {
                                                    for (var i = 0; i < ranges.length; i++) {
                                                       if (n >= ranges[i].divider) {
                                                          return (n / ranges[i].divider).toString() + ranges[i].suffix;
                                                       }
                                                    }
                                                    return n;
                                                 }
                                                 return '$ ' + formatNumber(value);
                                              }
                                        }
                                    }
                                ]
                            }
                        }
                    });
                }
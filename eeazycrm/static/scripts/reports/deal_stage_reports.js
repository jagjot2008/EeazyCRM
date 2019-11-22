function plot_deal_stage_report_price_bar_graph(labels, data) {
    var ctx = document.getElementById('myChart1').getContext('2d');
    var myChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: '# Deal Stages Price in USD',
                                data: data,
                                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                                borderColor: 'rgba(54, 162, 235, 0.85)',
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

function plot_deal_stage_report_count_bar_graph(labels, data) {
    var ctx = document.getElementById('myChart2').getContext('2d');
    var myChart = new Chart(ctx, {
                        type: 'bar',
                        data: {
                            labels: labels,
                            datasets: [{
                                label: '# Deal Stages deals count',
                                data: data,
                                backgroundColor: 'rgba(255, 99, 132, 0.5)',
                                borderColor: 'rgba(255, 99, 132, 0.85)',
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
                                            beginAtZero: true
                                        }
                                    }
                                ]
                            }
                        }
                    });
                }

function plot_deal_stage_report_price_pie_chart(labels, data) {
    var ctx = document.getElementById('myChart3').getContext('2d');
    var dynamicColors = function() {
        var r = Math.floor(Math.random() * 255);
        var g = Math.floor(Math.random() * 255);
        var b = Math.floor(Math.random() * 255);
        return "rgb(" + r + "," + g + "," + b + ", 0.55)";
    };

    colors = []
    for (var i=0; i < data.length; i++) {
        colors.push(dynamicColors());
    }

    var new_data = {
        datasets: [{
            data: data,
            backgroundColor: colors
        }],
        labels: labels
    }

    var myPieChart = new Chart(ctx, {
        type: 'pie',
        data: new_data,
        options: {
            cutoutPercentage: 0,
        }
    });
}
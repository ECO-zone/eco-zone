Highcharts.setOptions({
    colors: [
        '#058DC7', '#50B432', '#ED561B', '#DDDF00', '#24CBE5', '#64E572',
        '#FF9655', '#FFF263', '#6AF9C4'
    ],
    lang: {
        decimalPoint: ',',
        downloadCSV: 'CSV herunterladen',
        downloadJPEG: 'JPEG herunterladen',
        downloadMIDI: 'MIDI herunterladen',
        downloadPDF: 'PDF herunterladen',
        downloadPNG: 'PNG herunterladen',
        downloadSVG: 'SVG herunterladen',
        downloadXLS: 'XLS herunterladen',
        exitFullscreen: 'Vollbild-Ansicht deaktiveren',
        exportInProgress: "Exportieren...",
        hideData: 'Datentabelle verstecken',
        loading: 'Laden...',
        mainBreadcrumb: 'Main',
        months: [
            'Januar', 'Februar', 'März', 'April',
            'Mai', 'Juni', 'Juli', 'August',
            'September', 'Oktober', 'November', 'Dezember'
        ],
        numericSymbols: [' Tsd.', ' Mio.'],
        printChart: 'Diagramm drucken',
        resetZoom: 'Zoom zurücksetzen',
        resetZoomTitle: 'Zoom-Grad zurücksetzen 1:1',
        thousandsSep: ".",
        viewData: 'Datentabelle anschauen',
        viewFullscreen: 'Vollbild-Ansicht aktivieren',
        weekdays: [
            'Sonntag', 'Montag', 'Dienstag', 'Mittwoch',
            'Donnerstag', 'Freitag', 'Samstag'
        ],
        shortMonths: ['Jan', 'Feb', 'Mär', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Dez'],
    },
    plotOptions: {
        series: {
            animation: false
        }
    },
    time: {
        timezone: 'Europe/Berlin'
    }
});

Highcharts.chart('chart-timeseries-redispatch', {
    title: {
        text: 'Redispatch-Leistung als Timeseries',
        align: 'left'
    },

    subtitle: {
        text: 'Mittlere Leistung in MW pro Richtung. Hochrechnung durch ECO zone. Datenquelle: <a href="https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsf%C3%BChrung/Redispatch" target="_blank">Netztransparenz.de</a>.',
        align: 'left'
    },

    yAxis: {
        title: {
            text: 'Mittlere Leistung MW'
        }
    },

    xAxis: {
        title: {
            text: 'Auflösung: 15-Minuten'
        },
        accessibility: {
            rangeDescription: 'Auflösung: 15-Minuten'
        }
    },

    legend: {
        layout: 'horizontal',
        align: 'left',
        verticalAlign: 'bottom'
    },
    tooltip: {
        shared: true,
    },

    // plotOptions: {
    //     series: {
    //         label: {
    //             connectorAllowed: false
    //         },
    //         pointStart: 2010
    //     }
    // },

    // series: [{
    //     name: 'Installation & Developers',
    //     data: [
    //         43934, 48656, 65165, 81827, 112143, 142383,
    //         171533, 165174, 155157, 161454, 154610
    //     ]
    // }, {
    //     name: 'Manufacturing',
    //     data: [
    //         24916, 37941, 29742, 29851, 32490, 30282,
    //         38121, 36885, 33726, 34243, 31050
    //     ]
    // }, {
    //     name: 'Sales & Distribution',
    //     data: [
    //         11744, 30000, 16005, 19771, 20185, 24377,
    //         32147, 30912, 29243, 29213, 25663
    //     ]
    // }, {
    //     name: 'Operations & Maintenance',
    //     data: [
    //         null, null, null, null, null, null, null,
    //         null, 11164, 11218, 10077
    //     ]
    // }, {
    //     name: 'Other',
    //     data: [
    //         21908, 5548, 8105, 11248, 8989, 11816, 18274,
    //         17300, 13053, 11906, 10073
    //     ]
    // }],
    credits: {
        enabled: false,
    },
    data: {
        rowsURL: '/api/timeseries/redispatch?start=2024-01-01T00%3A00%2B01%3A00',
        complete: function (parsedData) {
            for (let series of parsedData.series) {
                let newName = {'power_mid_mw_decrease': 'Wirkleistungseinspeisung reduzieren', 'power_mid_mw_increase': 'Wirkleistungseinspeisung erhöhen'}[series.name]
                if (newName) {
                    series.name = newName;
                }
            }
        },
    },
    responsive: {
        rules: [{
            condition: {
                maxWidth: 500
            },
            chartOptions: {
                legend: {
                    layout: 'horizontal',
                    align: 'center',
                    verticalAlign: 'bottom'
                }
            }
        }]
    }

});

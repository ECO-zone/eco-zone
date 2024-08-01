Highcharts.setOptions({
  chart: {
    style: {
      fontFamily: "Source Sans 3",
    },
  },
  colors: [
    "#058DC7",
    "#50B432",
    "#ED561B",
    "#DDDF00",
    "#24CBE5",
    "#64E572",
    "#FF9655",
    "#FFF263",
    "#6AF9C4",
  ],
  lang: {
    decimalPoint: ",",
    downloadCSV: "CSV herunterladen",
    downloadJPEG: "JPEG herunterladen",
    downloadMIDI: "MIDI herunterladen",
    downloadPDF: "PDF herunterladen",
    downloadPNG: "PNG herunterladen",
    downloadSVG: "SVG herunterladen",
    downloadXLS: "XLS herunterladen",
    exitFullscreen: "Vollbild-Ansicht deaktiveren",
    exportInProgress: "Exportieren...",
    hideData: "Datentabelle verstecken",
    loading: "Laden...",
    mainBreadcrumb: "Main",
    months: [
      "Januar",
      "Februar",
      "März",
      "April",
      "Mai",
      "Juni",
      "Juli",
      "August",
      "September",
      "Oktober",
      "November",
      "Dezember",
    ],
    numericSymbols: [" Tsd.", " Mio."],
    printChart: "Diagramm drucken",
    resetZoom: "Zoom zurücksetzen",
    resetZoomTitle: "Zoom-Grad zurücksetzen 1:1",
    thousandsSep: ".",
    viewData: "Datentabelle anschauen",
    viewFullscreen: "Vollbild-Ansicht aktivieren",
    weekdays: [
      "Sonntag",
      "Montag",
      "Dienstag",
      "Mittwoch",
      "Donnerstag",
      "Freitag",
      "Samstag",
    ],
    shortMonths: [
      "Jan",
      "Feb",
      "Mär",
      "Apr",
      "Mai",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Okt",
      "Nov",
      "Dez",
    ],
  },
  plotOptions: {
    series: {
      animation: true,
    },
  },
  time: {
    timezone: "Europe/Berlin",
  },
});

function makeChart(config) {
  let chart = Highcharts.stockChart(config.id, {
    chart: {
      events: {
        load() {
          this.showLoading();
        },
        redraw() {
          this.hideLoading();
        },
      },
      height: 500,
      type: config.type,
    },
    credits: {
      enabled: false,
    },
    data: {
      rowsURL: config.url,
      complete: function (parsedData) {
        for (let series of parsedData.series) {
          let newName = config.seriesNames[series.name];
          if (newName) {
            series.name = newName;
          }
          series.showInNavigator = true;
          if (config.type === 'area') {
            series.label = false;
            series.stacking = "normal";
            series.type = "area";
          }
        }
      },
    },
    legend: {
      enabled: true,
      layout: "horizontal",
      align: "left",
      verticalAlign: "bottom",
    },
    loading: {
      hideDuration: 500,
      labelStyle: {"fontWeight": "bold", "position": "relative", "top": "-55%",},
      showDuration: 10,
      style: {"position": "relative", "backgroundColor": "#ffffff", "opacity": 0.7,}
    },
    navigator: {
      enabled: true,
      series: (config.type == "area") ? {stacking: "normal", type: "area", fillOpacity: 1,} : {}
    },
    rangeSelector: {
      buttons: [
        {
          type: 'month',
          count: 1,
          text: '1 Mo.',
          title: '1 Monat anzeigen'
        }, {
          type: 'month',
          count: 3,
          text: '3 Mo.',
          title: '3 Monate anzeigen'
        }, {
          type: 'month',
          count: 6,
          text: '6 Mo.',
          title: '6 Monate anzeigen'
        }, {
          type: 'ytd',
          text: 'YTD',
          title: 'Aktuellen Jahresverlauf anzeigen'
        }, {
          type: 'year',
          count: 1,
          text: '1 Jahr',
          title: '1 Jahr anzeigen'
        }, {
            type: 'all',
            text: 'Alles',
            title: 'Alles anzeigen'
        }
      ],
      selected: 0,
      verticalAlign: 'top',
      x: 0,
      y: 0
    },
    subtitle: {
      text: config.subtitleText,
      align: "left",
    },
    title: {
      text: config.titleText,
      align: "left",
    },
    tooltip: {
      shared: true,
      split: false,
      valueDecimals: 2,
    },
    xAxis: {
      title: {
        text: "Auflösung: 15-Minuten",
      },
      accessibility: {
        rangeDescription: "Auflösung: 15-Minuten",
      },
    },
    yAxis: {
      opposite: false,
      title: {
        text: config.yAxisText,
      },
    },
  });
  return chart;
}

function isVisibleInViewport(value) {
  let item = value.getBoundingClientRect();
  return item.top + 40 <= window.innerHeight
}

let generationChartEl = document.getElementById('chart-timeseries-generation');
let emissionsChartEl = document.getElementById('chart-timeseries-emissions');
let regionalEmissionsChartEl = document.getElementById('chart-timeseries-emissions-regional');


let emissionIntensityRegionalChart = makeChart({
  id: "chart-timeseries-emission-intensity-regional",
  type: "line",
  seriesNames: {
    emission_intensity: "Emissionsintensität",
    emission_intensity_north: "Emissionsintensität Regional [Nord]",
    emission_intensity_south: "Emissionsintensität Regional [Süd]",
  },
  subtitleText: 'Emissionsintensität [kgCO2/MWh]. Hochrechnung durch ECO zone anhand DIN SPEC 91410-2. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.eu</a>.',
  titleText: 'Emissionsintensität Regional als Timeseries',
  url: '/api/timeseries/emission-intensity-regional?region=north&start=2024-01-01T00%3A00%2B02%3A00',
  yAxisText: 'Emissionsintensität [kgCO2/MWh]',
});

let dropdownRegionSelect = document.getElementById('dropdown-region-select');
dropdownRegionSelect.addEventListener('change', function() {
  emissionIntensityRegionalChart.update({
    data: {
      rowsURL: `/api/timeseries/emission-intensity-regional?region=${this.value}&start=2024-01-01T00%3A00%2B02%3A00`
    }
  });
});

function makeGenerationChart() {
  if (isVisibleInViewport(generationChartEl) == true) {
    window.removeEventListener("scroll", makeGenerationChart)
    makeChart({
      id: "chart-timeseries-generation",
      type: "area",
      seriesNames: {
        B01: "Biomasse",
        B02: "Braunkohle",
        B04: "Erdgas",
        B05: "Steinkohle",
        B06: "Mineralöl",
        B09: "Geothermie",
        B10: "Pumpspeicher",
        B11: "Wasserkraft (Laufwasser)",
        B12: "Wasserspeicher",
        B15: "Sonstige Erneuerbare Energien",
        B16: "Photovoltaik",
        B17: "Abfall",
        B18: "Windenergie (Offshore-Anlage)",
        B19: "Windenergie (Onshore-Anlage)",
        B20: "Sonstige konventionelle Energien",
      },
      subtitleText: 'Nettostromerzeugung pro Energieträger. Hochrechnung durch ECO zone. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.eu</a>.',
      titleText: 'Nettostromerzeugung pro Energieträger als Timeseries',
      url: "/api/timeseries/generation?start=2024-01-01T00%3A00%2B02%3A00",
      yAxisText: 'Nettostromerzeugung [MW]',
    });
  }
}

function makeEmissionsChart() {
  if (isVisibleInViewport(emissionsChartEl) == true) {
    window.removeEventListener("scroll", makeEmissionsChart)
    makeChart({
      id: "chart-timeseries-emissions",
      type: "area",
      seriesNames: {
        B01: "Biomasse",
        B02: "Braunkohle",
        B04: "Erdgas",
        B05: "Steinkohle",
        B06: "Mineralöl",
        B09: "Geothermie",
        B10: "Pumpspeicher",
        B11: "Wasserkraft (Laufwasser)",
        B12: "Wasserspeicher",
        B15: "Sonstige Erneuerbare Energien",
        B16: "Photovoltaik",
        B17: "Abfall",
        B18: "Windenergie (Offshore-Anlage)",
        B19: "Windenergie (Onshore-Anlage)",
        B20: "Sonstige konventionelle Energien",
      },
      subtitleText: 'Emissionen pro Energieträger [kgCO2]. Hochrechnung durch ECO zone anhand DIN SPEC 91410-2. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.eu</a>.',
      titleText: 'Emissionen pro Energieträger als Timeseries',
      url: '/api/timeseries/emissions?start=2024-01-01T00%3A00%2B02%3A00',
      yAxisText: 'Emissionen [kgCO2]',
    });
  }
}

window.addEventListener('scroll', makeGenerationChart);
window.addEventListener('scroll', makeEmissionsChart);

makeChart({
  id: 'chart-timeseries-redispatch',
  type: "line",
  seriesNames: {
    power_mid_mw_decrease: "Wirkleistungseinspeisung reduzieren",
    power_mid_mw_increase: "Wirkleistungseinspeisung erhöhen",
  },
  subtitleText: 'Mittlere Leistung in MW pro Richtung. Hochrechnung durch ECO zone. Datenquelle: <a href="https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsf%C3%BChrung/Redispatch" target="_blank">Netztransparenz.de</a>.',
  titleText: 'Redispatch-Leistung als Timeseries',
  url: '/api/timeseries/redispatch?start=2024-01-01T00%3A00%2B02%3A00',
  yAxisText: 'Mittlere Leistung [MW]',
});

makeChart({
  id: "chart-timeseries-emission-intensity",
  type: "line",
  seriesNames: {
    emission_intensity: "Emissionsintensität",
  },
  subtitleText: 'Emissionsintensität [kgCO2/MWh]. Hochrechnung durch ECO zone anhand DIN SPEC 91410-2. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.eu</a>.',
  titleText: 'Emissionsintensität als Timeseries',
  url: '/api/timeseries/emission-intensity?start=2024-01-01T00%3A00%2B02%3A00',
  yAxisText: 'Emissionsintensität [kgCO2/MWh]',
});

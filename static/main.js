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

Highcharts.chart("chart-timeseries-redispatch", {
  credits: {
    enabled: false,
  },
  data: {
    rowsURL: "/api/timeseries/redispatch?start=2024-01-01T00%3A00%2B02%3A00",
    complete: function (parsedData) {
      for (let series of parsedData.series) {
        let newName = {
          power_mid_mw_decrease: "Wirkleistungseinspeisung reduzieren",
          power_mid_mw_increase: "Wirkleistungseinspeisung erhöhen",
        }[series.name];
        if (newName) {
          series.name = newName;
        }
      }
    },
  },
  legend: {
    layout: "horizontal",
    align: "left",
    verticalAlign: "bottom",
  },
  subtitle: {
    text: 'Mittlere Leistung in MW pro Richtung. Hochrechnung durch ECO zone. Datenquelle: <a href="https://www.netztransparenz.de/de-de/Systemdienstleistungen/Betriebsf%C3%BChrung/Redispatch" target="_blank">Netztransparenz.de</a>.',
    align: "left",
  },
  title: {
    text: "Redispatch-Leistung als Timeseries",
    align: "left",
  },
  tooltip: {
    shared: true,
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
    title: {
      text: "Mittlere Leistung [MW]",
    },
  },
});

Highcharts.chart("chart-timeseries-emission-intensity", {
  credits: {
    enabled: false,
  },
  data: {
    rowsURL: "/api/timeseries/emission-intensity?start=2024-01-01T00%3A00%2B02%3A00",
    complete: function (parsedData) {
      for (let series of parsedData.series) {
        let newName = {
          emission_intensity: "Emissionsintensität",
        }[series.name];
        if (newName) {
          series.name = newName;
        }
      }
    },
  },
  legend: {
    layout: "horizontal",
    align: "left",
    verticalAlign: "bottom",
  },
  subtitle: {
    text: 'Emissionsintensität [kgCO2/MWh]. Hochrechnung durch ECO zone anhand DIN SPEC 91410-2. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.de</a>.',
    align: "left",
  },
  title: {
    text: "Emissionsintensität als Timeseries",
    align: "left",
  },
  tooltip: {
    shared: true,
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
    title: {
      text: "Emissionsintensität [kgCO2/MWh]",
    },
  },
});

Highcharts.chart("chart-timeseries-generation", {
  chart: {
    type: "area",
  },
  credits: {
    enabled: false,
  },
  data: {
    rowsURL: "/api/timeseries/generation?start=2024-01-01T00%3A00%2B02%3A00",
    complete: function (parsedData) {
      for (let series of parsedData.series) {
        let newName = {
          B01: "Biomasse",
          B02: "Braunkohle",
          // B03: "Fossil Coal-derived gas",
          B04: "Erdgas",
          B05: "Steinkohle",
          B06: "Mineralöl",
          // B07: "Fossil Oil shale",
          // B08: "Fossil Peat",
          B09: "Geothermie",
          B10: "Pumpspeicher",
          B11: "Wasserkraft (Laufwasser)",
          B12: "Wasserspeicher",
          // B13: "Marine",
          // B14: "Kernenergie",
          B15: "Sonstige Erneuerbare Energien",
          B16: "Photovoltaik",
          B17: "Abfall",
          B18: "Windenergie (Offshore-Anlage)",
          B19: "Windenergie (Onshore-Anlage)",
          B20: "Sonstige konventionelle Energien",
        }[series.name];
        if (newName) {
          series.name = newName;
        }
        series.label = false;
        series.stacking = "normal";
        series.type = "area";
      }
    },
  },
  legend: {
    layout: "horizontal",
    align: "left",
    verticalAlign: "bottom",
  },
  subtitle: {
    text: 'Nettostromerzeugung pro Energieträger. Hochrechnung durch ECO zone. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.de</a>.',
    align: "left",
  },
  title: {
    text: "Nettostromerzeugung pro Energieträger als Timeseries",
    align: "left",
  },
  tooltip: {
    shared: true,
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
    title: {
      text: "Nettostromerzeugung [MW]",
    },
  },
});

Highcharts.chart("chart-timeseries-emissions", {
  chart: {
    type: "area",
  },
  credits: {
    enabled: false,
  },
  data: {
    rowsURL: "/api/timeseries/emissions?start=2024-01-01T00%3A00%2B02%3A00",
    complete: function (parsedData) {
      for (let series of parsedData.series) {
        let newName = {
          B01: "Biomasse",
          B02: "Braunkohle",
          // B03: "Fossil Coal-derived gas",
          B04: "Erdgas",
          B05: "Steinkohle",
          B06: "Mineralöl",
          // B07: "Fossil Oil shale",
          // B08: "Fossil Peat",
          B09: "Geothermie",
          B10: "Pumpspeicher",
          B11: "Wasserkraft (Laufwasser)",
          B12: "Wasserspeicher",
          // B13: "Marine",
          // B14: "Kernenergie",
          B15: "Sonstige Erneuerbare Energien",
          B16: "Photovoltaik",
          B17: "Abfall",
          B18: "Windenergie (Offshore-Anlage)",
          B19: "Windenergie (Onshore-Anlage)",
          B20: "Sonstige konventionelle Energien",
        }[series.name];
        if (newName) {
          series.name = newName;
        }
        series.label = false;
        series.stacking = "normal";
        series.type = "area";
      }
    },
  },
  legend: {
    layout: "horizontal",
    align: "left",
    verticalAlign: "bottom",
  },
  subtitle: {
    text: 'Emissionen pro Energieträger [kgCO2]. Hochrechnung durch ECO zone anhand DIN SPEC 91410-2. Datenquelle: <a href="https://transparency.entsoe.eu/generation/r2/actualGenerationPerProductionType" target="_blank">transparency.entsoe.de</a>.',
    align: "left",
  },
  title: {
    text: "Emissionen pro Energieträger als Timeseries",
    align: "left",
  },
  tooltip: {
    shared: true,
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
    title: {
      text: "Emissionen [kgCO2]",
    },
  },
});

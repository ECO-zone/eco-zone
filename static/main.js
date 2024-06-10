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
    rowsURL: "/api/timeseries/redispatch?start=2024-01-01T00%3A00%2B01%3A00",
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
      text: "Mittlere Leistung MW",
    },
  },
});

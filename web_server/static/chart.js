const socket = io.connect('http://localhost:5000');

socket.on('connect', () => {
    console.log('Connected to WebSocket server');
});

socket.on('chart_update', (data) => {
    console.log('Received chart update:', data);
    const chartData = JSON.parse(data);
    const klines = chartData.klines.klines;
    const openOrders = chartData.open_orders;
    const executedTrades = chartData.executed_trades;

    const timestamps = klines.map(k => new Date(parseInt(k[0])));
    const opens = klines.map(k => parseFloat(k[1]));
    const highs = klines.map(k => parseFloat(k[2]));
    const lows = klines.map(k => parseFloat(k[3]));
    const closes = klines.map(k => parseFloat(k[4]));
    const volumes = klines.map(k => parseFloat(k[5]));

    const volumeColors = closes.map((close, i) => close >= opens[i] ? 'green' : 'red');

    const fig = {
        data: [
            {
                x: timestamps,
                open: opens,
                high: highs,
                low: lows,
                close: closes,
                type: 'candlestick',
                name: 'Klines',
                xaxis: 'x',
                yaxis: 'y'
            },
            {
                x: timestamps,
                y: volumes,
                type: 'bar',
                marker: { color: volumeColors },
                name: 'Volume',
                xaxis: 'x2',
                yaxis: 'y2'
            }
        ],
        layout: {
            title: 'Dynamic Kline Chart',
            grid: { rows: 2, columns: 1, pattern: 'independent' },
            xaxis: { domain: [0, 1] },
            yaxis: { title: 'Price' },
            xaxis2: { anchor: 'y2' },
            yaxis2: { title: 'Volume', domain: [0, 0.2] },
            height: 800,
            margin: { l: 50, r: 50, t: 50, b: 50 },
            template: 'plotly_dark'
        }
    };

    openOrders.forEach(order => {
        const price = parseFloat(order.price);
        const side = order.side;
        const quantity = parseFloat(order.quantity);
        const color = side === 'sell' ? 'red' : 'green';
        fig.data.push({
            x: [timestamps[0], timestamps[timestamps.length - 1]],
            y: [price, price],
            mode: 'lines',
            line: { color: color, dash: 'dash', width: 4 },
            showlegend: false,
            xaxis: 'x',
            yaxis: 'y'
        });
        fig.layout.annotations = fig.layout.annotations || [];
        fig.layout.annotations.push({
            x: timestamps[timestamps.length - 1],
            y: price,
            text: `${side.charAt(0).toUpperCase() + side.slice(1)} ${price.toFixed(4)} (${quantity.toFixed(2)})`,
            showarrow: false,
            font: { color: 'white', size: 10 },
            bgcolor: 'black',
            bordercolor: 'black',
            borderwidth: 1,
            xshift: 10
        });
        fig.data.push({
            x: [timestamps[timestamps.length - 1]],
            y: [side === 'buy' ? price + 0.00005 : price - 0.00005],
            mode: 'markers',
            marker: { symbol: side === 'buy' ? 'triangle-up' : 'triangle-down', size: 10, color: color },
            showlegend: false,
            xaxis: 'x',
            yaxis: 'y'
        });
    });

    executedTrades.forEach(trade => {
        const price = parseFloat(trade.price);
        const side = trade.side;
        const color = side === 'sell' ? 'red' : 'green';
        const timestamp = new Date(parseInt(trade.timestamp));
        fig.data.push({
            x: [timestamp],
            y: [side === 'buy' ? price + 0.00005 : price - 0.00005],
            mode: 'markers',
            marker: { symbol: side === 'buy' ? 'triangle-up' : 'triangle-down', size: 10, color: color },
            showlegend: false,
            xaxis: 'x',
            yaxis: 'y'
        });
    });

    Plotly.newPlot('dynamic-chart', fig.data, fig.layout);
});

socket.on('disconnect', () => {
    console.log('Disconnected from WebSocket server');
});

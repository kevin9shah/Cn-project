document.addEventListener('DOMContentLoaded', function () {
    const deviceList = document.getElementById('device-list');
    const addDeviceForm = document.getElementById('add-device-form');

    const charts = {};
    const chartConfigs = {
        'rtt-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'RTT (ms)'
                        }
                    }
                }
            }
        },
        'jitter-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Jitter (ms)'
                        }
                    }
                }
            }
        },
        'packet-loss-chart': {
            type: 'line',
            data: {
                labels: [],
                datasets: []
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        title: {
                            display: true,
                            text: 'Packet Loss (%)'
                        }
                    }
                }
            }
        }
    };

    function createChart(chartId) {
        const ctx = document.getElementById(chartId).getContext('2d');
        charts[chartId] = new Chart(ctx, chartConfigs[chartId]);
    }

    Object.keys(chartConfigs).forEach(createChart);

    const socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('new_data', (data) => {
        updateDeviceCard(data);
        updateCharts(data);
    });

    async function fetchDevices() {
        const response = await fetch('/api/status');
        const devices = await response.json();
        deviceList.innerHTML = '';
        devices.forEach(device => {
            createDeviceCard(device);
            addDeviceToCharts(device);
        });
    }

    function createDeviceCard(device) {
        const card = document.createElement('div');
        card.className = 'col-md-6';
        card.innerHTML = `
            <div id="device-card-${device.id}" class="device-card status-${device.status ? device.status.toLowerCase() : 'unknown'}">
                <h5>${device.name}</h5>
                <p>${device.ip_address}</p>
                <p>Status: <span class="status-badge">${device.status || 'UNKNOWN'}</span></p>
                <p>Last Checked: <span class="last-checked">${device.last_checked ? new Date(device.last_checked).toLocaleString() : 'N/A'}</span></p>
                <button class="btn btn-sm btn-danger" onclick="deleteDevice(${device.id})">Delete</button>
            </div>
        `;
        deviceList.appendChild(card);
        card.addEventListener('click', () => showDeviceHistory(device));
    }

    let selectedDevice = null;

    async function showDeviceHistory(device) {
        selectedDevice = device;
        const response = await fetch(`/api/devices/${device.id}/history`);
        const history = await response.json();

        Object.keys(charts).forEach(chartId => {
            const chart = charts[chartId];
            chart.data.labels = [];
            chart.data.datasets = [];

            const deviceColor = `hsl(${device.id * 40}, 70%, 50%)`;
            const dataset = {
                label: device.name,
                data: [],
                borderColor: deviceColor,
                tension: 0.1
            };

            history.forEach(ping => {
                chart.data.labels.push(new Date(ping.timestamp).toLocaleTimeString());
                let value;
                if (chartId === 'rtt-chart') value = ping.rtt_ms;
                if (chartId === 'jitter-chart') value = ping.jitter;
                if (chartId === 'packet-loss-chart') value = ping.packet_loss;
                dataset.data.push(value);
            });

            chart.data.datasets.push(dataset);
            chart.update();
        });
    }

    function updateDeviceCard(data) {
        const card = document.getElementById(`device-card-${data.device_id}`);
        if (card) {
            card.className = `device-card status-${data.status.toLowerCase()}`;
            card.querySelector('.status-badge').textContent = data.status;
            card.querySelector('.last-checked').textContent = new Date(data.timestamp).toLocaleString();
        }
    }

    function addDeviceToCharts(device) {
        // Do nothing, charts are populated on click
    }

    function updateCharts(data) {
        if (selectedDevice && data.device_id === selectedDevice.id) {
            const now = new Date(data.timestamp).toLocaleTimeString();

            Object.keys(charts).forEach(chartId => {
                const chart = charts[chartId];
                const dataset = chart.data.datasets.find(ds => ds.label === selectedDevice.name);

                if (dataset) {
                    chart.data.labels.push(now);
                    if (chart.data.labels.length > 20) {
                        chart.data.labels.shift();
                    }

                    let value;
                    if (chartId === 'rtt-chart') value = data.rtt_ms;
                    if (chartId === 'jitter-chart') value = data.jitter;
                    if (chartId === 'packet-loss-chart') value = data.packet_loss;

                    dataset.data.push(value);
                    if (dataset.data.length > 20) {
                        dataset.data.shift();
                    }
                    chart.update();
                }
            });
        }
    }

    addDeviceForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const name = document.getElementById('name').value;
        const ip_address = document.getElementById('ip_address').value;
        const priority = document.getElementById('priority').value;

        const response = await fetch('/api/devices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, ip_address, priority })
        });

        if (response.ok) {
            const device = await response.json();
            createDeviceCard(device);
            addDeviceToCharts(device);
            addDeviceForm.reset();
        } else {
            alert('Failed to add device. Check API Key and server logs.');
        }
    });

    window.deleteDevice = async function (id) {
        if (confirm("Are you sure you want to delete this device?")) {
            const response = await fetch(`/api/devices/${id}`, {
                method: 'DELETE',
                headers: {
                }
            });
            if (response.ok) {
                document.getElementById(`device-card-${id}`).parentElement.remove();
            } else {
                alert("Failed to delete device. Check API Key and server logs.");
            }
        }
    }

    fetchDevices();
});

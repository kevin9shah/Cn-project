document.addEventListener('DOMContentLoaded', function () {
    const deviceList = document.getElementById('device-list');
    const addDeviceForm = document.getElementById('add-device-form');
    const apiKey = prompt("Enter API Key");

    let chart;

    async function fetchDevices() {
        const response = await fetch('/api/status');
        const devices = await response.json();
        deviceList.innerHTML = '';
        devices.forEach(device => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${device.name}</td>
                <td>${device.ip_address}</td>
                <td><span class="badge bg-${device.status === 'UP' ? 'success' : 'danger'}">${device.status}</span></td>
                <td>${device.last_checked ? new Date(device.last_checked).toLocaleString() : 'N/A'}</td>
                <td>
                    <button class="btn btn-sm btn-info" onclick="viewHistory(${device.id})">History</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteDevice(${device.id})">Delete</button>
                </td>
            `;
            deviceList.appendChild(row);
        });
    }

    addDeviceForm.addEventListener('submit', async function (event) {
        event.preventDefault();
        const name = document.getElementById('name').value;
        const ip_address = document.getElementById('ip_address').value;
        const priority = document.getElementById('priority').value;

        await fetch('/api/devices', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': apiKey
            },
            body: JSON.stringify({ name, ip_address, priority })
        });
        addDeviceForm.reset();
        fetchDevices();
    });

    window.deleteDevice = async function (id) {
        if (confirm("Are you sure you want to delete this device?")) {
            const response = await fetch(`/api/devices/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-API-KEY': apiKey
                }
            });
            if (response.ok) {
                fetchDevices();
            } else {
                alert("Failed to delete device. Check API Key and server logs.");
            }
        }
    }

    window.viewHistory = async function (id) {
        const response = await fetch(`/api/devices/${id}/history`);
        const history = await response.json();

        const labels = history.map(p => new Date(p.timestamp).toLocaleTimeString());
        const data = history.map(p => p.rtt_ms);

        if (chart) {
            chart.destroy();
        }

        const ctx = document.getElementById('ping-chart').getContext('2d');
        chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels.reverse(),
                datasets: [{
                    label: 'Response Time (ms)',
                    data: data.reverse(),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            }
        });
    }


    fetchDevices();
    setInterval(fetchDevices, 5001);
});

document.addEventListener('DOMContentLoaded', () => {
    // DOM 元素引用
    const queryForm = document.getElementById('query-form');
    const pollutantSelect = document.getElementById('pollutant-select');
    const limitInput = document.getElementById('limit-input');
    const statusMessage = document.getElementById('status-message');
    
    const dataSection = document.getElementById('data-section');
    const mapSection = document.getElementById('map-section');
    const chartSection = document.getElementById('chart-section');
    
    const dataTableBody = document.querySelector('#data-table tbody');
    const dataTableHeader = document.querySelector('#data-table thead');
    const mapContainer = document.getElementById('map-container');
    const chartContainer = document.getElementById('chart-container');

    // 初始化地图
    let map = null;
    let mapMarkers = null;
    
    function initMap() {
        if (map) return; // 如果地图已初始化，则不重复执行
        map = L.map(mapContainer).setView([45.4642, 9.1900], 8);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(map);
        mapMarkers = L.layerGroup().addTo(map);
    }

    // 显示状态消息的辅助函数
    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = `status-message ${type} visible`;
    }

    // 1. 页面加载时，填充污染物下拉菜单
    async function populatePollutants() {
        try {
            const response = await fetch('/api/pollutants');
            if (!response.ok) throw new Error('Failed to load pollutants');
            
            const pollutants = await response.json();
            pollutantSelect.innerHTML = '<option value="">-- Select a Pollutant --</option>';
            pollutants.forEach(p => {
                const option = document.createElement('option');
                option.value = p;
                option.textContent = p;
                pollutantSelect.appendChild(option);
            });
        } catch (error) {
            showStatus(error.message, 'error');
        }
    }

    // 2. 表单提交事件处理
    queryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pollutant = pollutantSelect.value;
        const limit = limitInput.value;

        if (!pollutant) {
            showStatus('Please select a pollutant.', 'error');
            return;
        }

        showStatus(`Fetching data for ${pollutant}...`, 'info');

        try {
            // 从 API 获取数据
            const url = `/api/measurements?pollutant=${encodeURIComponent(pollutant)}&limit=${limit}`;
            const response = await fetch(url);
            if (!response.ok) throw new Error('Failed to fetch data');

            const data = await response.json();
            showStatus(`Successfully fetched ${data.length} records.`, 'success');

            if (data.length === 0) {
                // 如果没有数据，隐藏内容区域
                dataSection.style.display = 'none';
                mapSection.style.display = 'none';
                chartSection.style.display = 'none';
                return;
            }

            // 显示内容区域
            dataSection.style.display = 'block';
            mapSection.style.display = 'block';
            chartSection.style.display = 'block';

            // 更新所有可视化内容
            updateTable(data);
            updateMap(data);
            updateChart(data, pollutant);

        } catch (error) {
            showStatus(error.message, 'error');
        }
    });

    // 3. 更新数据表格
    function updateTable(data) {
        // 清空旧数据
        dataTableHeader.innerHTML = '';
        dataTableBody.innerHTML = '';

        if (data.length === 0) return;

        // 创建表头
        const headers = ['Timestamp', 'Station', 'Pollutant', 'Value'];
        const headerRow = document.createElement('tr');
        headers.forEach(headerText => {
            const th = document.createElement('th');
            th.textContent = headerText;
            headerRow.appendChild(th);
        });
        dataTableHeader.appendChild(headerRow);

        // 填充数据行
        data.forEach(item => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${new Date(item.timestamp).toLocaleString()}</td>
                <td>${item.station_name}</td>
                <td>${item.pollutant}</td>
                <td>${item.value.toFixed(2)}</td>
            `;
            dataTableBody.appendChild(row);
        });
    }

    // 4. 更新地图
    function updateMap(data) {
        initMap(); // 确保地图已初始化
        mapMarkers.clearLayers(); // 清空旧标记

        const locations = [];
        data.forEach(item => {
            const { coordinates } = item.location;
            const lat = coordinates[1];
            const lon = coordinates[0];
            locations.push([lat, lon]);
            
            const popupText = `<b>Station:</b> ${item.station_name}<br><b>Value:</b> ${item.value.toFixed(2)}`;
            L.marker([lat, lon]).addTo(mapMarkers).bindPopup(popupText);
        });
        
        // 自动缩放到所有标记的范围
        if (locations.length > 0) {
            map.fitBounds(locations);
        }
    }

    // 5. 更新图表
    function updateChart(data, pollutant) {
        const traces = {};
        data.forEach(item => {
            if (!traces[item.station_name]) {
                traces[item.station_name] = { x: [], y: [], mode: 'lines+markers', name: item.station_name };
            }
            traces[item.station_name].x.push(item.timestamp);
            traces[item.station_name].y.push(item.value);
        });

        const plotData = Object.values(traces);
        const layout = {
            title: `Time Series for ${pollutant}`,
            xaxis: { title: 'Timestamp' },
            yaxis: { title: 'Measurement Value (µg/m³)' },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)',
            font: { color: 'white' }
        };

        Plotly.newPlot(chartContainer, plotData, layout, {responsive: true});
    }

    // 初始化页面
    populatePollutants();
});
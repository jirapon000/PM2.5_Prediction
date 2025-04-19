async function fetchPollutionData() {
    try {
        const response = await fetch('/get_station_pollution_data');
        const data = await response.json();

        const tableBody = document.getElementById("station-table");
        tableBody.innerHTML = ''; // Clear existing rows

        data.forEach((station, index) => {
            const row = document.createElement('tr');
            
            // Rank Column
            const rankCell = document.createElement('td');
            rankCell.innerText = index + 1;
            row.appendChild(rankCell);
            
            // Station Column
            const stationCell = document.createElement('td');
            stationCell.innerHTML = `<img src="static/Thailand_flag.png" alt="Flag" width="20px"> ${station.station}`;
            row.appendChild(stationCell);
            
            // PM2.5 Column
            const pm25Cell = document.createElement('td');
            pm25Cell.innerText = station.pm2_5 ? station.pm2_5 : "No data";
            row.appendChild(pm25Cell);
            
            // PM2.5 Status Column
            const pm25StatusCell = document.createElement('td');
            let statusColor = "black";
            let statusText = "No data";
            
            if (station.pm2_5) {
                if (station.pm2_5 <= 38) {
                    statusText = "Good";
                    statusColor = "green";
                } else if (station.pm2_5 > 38 && station.pm2_5 <= 50) {
                    statusText = "Moderate";
                    statusColor = "orange";
                } else {
                    statusText = "Severe";
                    statusColor = "red";
                }
            }
            
            pm25StatusCell.innerHTML = `<span style="color: ${statusColor};">${statusText}</span>`;
            row.appendChild(pm25StatusCell);
            
            // Standard Value Column
            const standardCell = document.createElement('td');
            standardCell.innerText = station.pm2_5 ? `${(station.pm2_5 / 50).toFixed(1)}x above Standard` : "N/A";
            row.appendChild(standardCell);
            
            // Follow Column
            const followCell = document.createElement('td');
            const followButton = document.createElement('button');
            followButton.innerText = "❤️ Follow";
            followCell.appendChild(followButton);
            row.appendChild(followCell);
            
            // Append the row to the table body
            tableBody.appendChild(row);
        });
    } catch (error) {
        console.error("Error fetching pollution data:", error);
    }
}

// Call the function when the page loads
window.onload = fetchPollutionData;

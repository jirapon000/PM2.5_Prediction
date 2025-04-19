async function fetchPollutionData() {
    try {
        // Fetch data from the backend
        const response = await fetch('/get_pollution_data');
        const data = await response.json();

        // Check if data is valid
        console.log("Fetched Data:", data);

        // Update PM2.5 value
        if (data && data.pm2_5) {
            const pm25Value = document.getElementById("pm25-value");
            pm25Value.innerText = `${data.pm2_5} µg/m³`;
            pm25Value.style.color = data.pm2_5 <= 38 ? "green" : data.pm2_5 <= 50 ? "orange" : "red";
        } else {
            document.getElementById("pm25-value").innerText = "Data not available";
        }

        // Update PM10 value
        if (data && data.pm10) {
            const pm10Value = document.getElementById("pm10-value");
            pm10Value.innerText = `${data.pm10} µg/m³`;
            pm10Value.style.color = data.pm10 <= 38 ? "green" : data.pm10 <= 50 ? "orange" : "red";
        } else {
            document.getElementById("pm10-value").innerText = "Data not available";
        }

        // Update SO2 value
        if (data && data.so2) {
            const so2Value = document.getElementById("so2-value");
            so2Value.innerText = `${data.so2} ppb`;
            so2Value.style.color = data.so2 <= 5 ? "green" : data.so2 <= 15 ? "orange" : "red";
        } else {
            document.getElementById("so2-value").innerText = "Data not available";
        }

        // Update NO2 value
        if (data && data.no2) {
            const no2Value = document.getElementById("no2-value");
            no2Value.innerText = `${data.no2} ppb`;
            no2Value.style.color = data.no2 <= 40 ? "green" : data.no2 <= 100 ? "orange" : "red";
        } else {
            document.getElementById("no2-value").innerText = "Data not available";
        }

        // Update Temperature value (handle null value)
        const temperatureValue = document.getElementById("temperature-value");
        if (data && data.temperature !== null) {
            temperatureValue.innerText = `${data.temperature} °C`;
            temperatureValue.style.color = data.temperature <= 0 ? "blue" : data.temperature <= 25 ? "green" : "red";
        } else {
            temperatureValue.innerText = "Temperature data not available";
        }

    } catch (error) {
        console.error("Error fetching pollution data:", error);
        document.getElementById("pm25-value").innerText = "Failed to load data";
        document.getElementById("pm10-value").innerText = "Failed to load data";
        document.getElementById("so2-value").innerText = "Failed to load data";
        document.getElementById("no2-value").innerText = "Failed to load data";
        document.getElementById("temperature-value").innerText = "Failed to load data";
    }
}

// Call the function when the page loads
window.onload = fetchPollutionData;



// async function fetchPollutionData() {
//     try {
//         // Assuming you're calling your backend API to get this data
//         const response = await fetch('/get_pollution_data');  // Change this to your actual API endpoint
//         const data = await response.json();

//         // Update PM2.5 value
//         if (data && data.pm2_5) {
//             const pm25Value = document.getElementById("pm25-value");
//             pm25Value.innerText = `${data.pm2_5} µg/m³`;

//             // Change the color based on PM2.5 level
//             if (data.pm2_5 <= 38) {
//                 pm25Value.style.color = "green"; // Good air quality
//             } else if (data.pm2_5 >= 38 && data.pm2_5 <= 50) {
//                 pm25Value.style.color = "orange"; // Moderate air quality
//             } else {
//                 pm25Value.style.color = "red"; // Unhealthy air quality
//             }
//         } else {
//             document.getElementById("pm25-value").innerText = "Data not available";
//         }

//         // Update PM10 value
//         if (data && data.pm10) {
//             const pm10Value = document.getElementById("pm10-value");
//             pm10Value.innerText = `${data.pm10} µg/m³`;

//             // Change the color based on PM10 level
//             if (data.pm10 <= 38) {
//                 pm10Value.style.color = "green"; // Good air quality
//             } else if (data.pm10 >= 38 && data.pm2_5 <= 50) {
//                 pm10Value.style.color = "orange"; // Moderate air quality
//             } else {
//                 pm10Value.style.color = "red"; // Unhealthy air quality
//             }
//         } else {
//             document.getElementById("pm10-value").innerText = "Data not available";
//         }

//         // Update SO2 value
//         if (data && data.so2) {
//             const so2Value = document.getElementById("so2-value");
//             so2Value.innerText = `${data.so2} ppb`;

//             // Change the color based on SO2 level
//             if (data.so2 <= 5) {
//                 so2Value.style.color = "green"; // Good air quality
//             } else if (data.so2 <= 15) {
//                 so2Value.style.color = "orange"; // Moderate air quality
//             } else {
//                 so2Value.style.color = "red"; // Unhealthy air quality
//             }
//         } else {
//             document.getElementById("so2-value").innerText = "Data not available";
//         }

//         // Update NO2 value
//         if (data && data.no2) {
//             const no2Value = document.getElementById("no2-value");
//             no2Value.innerText = `${data.no2} ppb`;

//             // Change the color based on NO2 level
//             if (data.no2 <= 40) {
//                 no2Value.style.color = "green"; // Good air quality
//             } else if (data.no2 <= 100) {
//                 no2Value.style.color = "orange"; // Moderate air quality
//             } else {
//                 no2Value.style.color = "red"; // Unhealthy air quality
//             }
//         } else {
//             document.getElementById("no2-value").innerText = "Data not available";
//         }

//         // Update Temperature value (moved to the last one as requested)
//         if (data && data.temperature) {
//             const temperatureValue = document.getElementById("temperature-value");
//             temperatureValue.innerText = `${data.temperature} °C`;

//             // Change the color based on Temperature
//             if (data.temperature <= 0) {
//                 temperatureValue.style.color = "blue"; // Cold
//             } else if (data.temperature <= 25) {
//                 temperatureValue.style.color = "green"; // Moderate
//             } else {
//                 temperatureValue.style.color = "red"; // Hot
//             }
//         } else {
//             document.getElementById("temperature-value").innerText = "Data not available";
//         }

//     } catch (error) {
//         console.error("Error fetching pollution data:", error);
//         document.getElementById("pm25-value").innerText = "Failed to load data";
//         document.getElementById("pm10-value").innerText = "Failed to load data";
//         document.getElementById("so2-value").innerText = "Failed to load data";
//         document.getElementById("no2-value").innerText = "Failed to load data";
//         document.getElementById("temperature-value").innerText = "Failed to load data";
//     }
// }

// // Call fetchPollutionData when the page loads
// window.onload = fetchPollutionData;
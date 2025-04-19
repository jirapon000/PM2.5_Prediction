from flask import Flask, render_template, request, jsonify
import random
from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
import pickle
from joblib import load
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
from xgboost import XGBRegressor
import pytz

app = Flask(__name__)

# --------------------------------------------------------------------
# 1. Load Models and Column Order
# --------------------------------------------------------------------
def load_model(file_path):
    try:
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    except Exception as e:
        print(f"Failed to load model {file_path}: {e}")
        return None

# Load the scaler and XGBoost model (adjust filenames as needed)
scaler = load("saved_model/scaler.pkl")
model = load("saved_model/best_xgb_model.pkl")  # adjust file name if necessary

# Load the expected feature column order (log_col_order is a list)
log_col_order = load("saved_model/log_col_order.pkl")
# Expected order example (for reference):
# ['temp',
#  'population_density',
#  'factory_area',
#  'season_Cool Season',
#  'season_Hot Season',
#  'season_Rainy Season',
#  'pm10_log',
#  'so2_log',
#  'no2_log',
#  'co_log',
#  'o3_log']

# --------------------------------------------------------------------
# 2. Global Settings / Station Definitions
# --------------------------------------------------------------------
api_key = 'a693b748d40c2a70d69295b2caad893a'
city_name = 'Bangkok,TH'

stations = [
    {'name': 'Ratchathewi Station', 'lat': 13.7563, 'lon': 100.5018},
    {'name': 'Pathum Wan Station Station', 'lat': 13.7367, 'lon': 100.5231},
    {'name': 'Ladkrabang Station', 'lat': 13.7291, 'lon': 100.7750},
    {'name': 'Bang Na Station', 'lat': 13.6796, 'lon': 100.6067},
    {'name': 'Bang Khae Station', 'lat': 13.7083, 'lon': 100.3728},
    {'name': 'Taling Chan Station', 'lat': 13.7898, 'lon': 100.4486},
    {'name': 'Bang Sue Station', 'lat': 13.8225, 'lon': 100.5147}
]

stations_for_prediction = [
    {'name': 'Ratchathewi Station', 'lat': 13.7563, 'lon': 100.5018, 'population_density': 9046.87,  'factory_area': 123059},
    {'name': 'Pathum Wan Station Station', 'lat': 13.7367, 'lon': 100.5231, 'population_density': 4788.74,  'factory_area': 54185},
    {'name': 'Ladkrabang Station', 'lat': 13.7291, 'lon': 100.7750, 'population_density': 1452.45,  'factory_area': 4770457},
    {'name': 'Bang Na Station', 'lat': 13.6796, 'lon': 100.6067, 'population_density': 4542.29,  'factory_area': 631723},
    {'name': 'Bang Khae Station', 'lat': 13.7083, 'lon': 100.3728, 'population_density': 4324.14,  'factory_area': 1148799},
    {'name': 'Taling Chan Station', 'lat': 13.7898, 'lon': 100.4486, 'population_density': 3437.36,  'factory_area': 144736},
    {'name': 'Bang Sue Station', 'lat': 13.8225, 'lon': 100.5147, 'population_density': 10275.79, 'factory_area': 297638}
]

# --------------------------------------------------------------------
# 3. Utility Functions
# --------------------------------------------------------------------
def map_season(month):
    """Return season based on month (Bangkok)."""
    if 3 <= month <= 4:
        return 'Hot Season'
    elif 5 <= month <= 10:
        return 'Rainy Season'
    else:
        return 'Cool Season'

def fetch_data(api_key, stations):
    all_data = []
    for station in stations:
        pollution_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={station['lat']}&lon={station['lon']}&appid={api_key}"
        )
        response = requests.get(pollution_url)
        data = response.json()
        if 'list' not in data or not data['list']:
            print(f"No data available for station {station['name']}")
            continue
        
        entry = data['list'][0]
        dt = pd.to_datetime(entry['dt'], unit='s')
        components = entry.get('components', {})
        entry_data = {
            'datetime': dt.isoformat(),
            'station': station['name'],
            'lat': station['lat'],
            'lon': station['lon'],
            'pm2_5': components.get('pm2_5'),
            'pm10': components.get('pm10'),
            'so2': components.get('so2'),
            'no2': components.get('no2'),
            'o3': components.get('o3'),
            'co': components.get('co'),
        }
        all_data.append(entry_data)
    return pd.DataFrame(all_data)

def fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30]):
    all_data = []
    now = pd.Timestamp.now()
    for station in stations:
        for days in days_list:
            start_timestamp = int((now - pd.Timedelta(days=days)).timestamp())
            end_timestamp = int(now.timestamp())
            
            pollution_url = (
                f'http://api.openweathermap.org/data/2.5/air_pollution/history?'
                f'lat={station["lat"]}&lon={station["lon"]}&start={start_timestamp}&end={end_timestamp}&appid={api_key}'
            )
            response = requests.get(pollution_url)
            data = response.json()
            if 'list' not in data:
                print(f"No data for station {station['name']} for last {days} days")
                continue

            temp_data = []
            for entry in data['list']:
                dt = pd.to_datetime(entry['dt'], unit='s')
                components = entry.get('components', {})
                temp_data.append({
                    'datetime': dt.isoformat(),
                    'station': station['name'],
                    'lat': station['lat'],
                    'lon': station['lon'],
                    'pm2_5': components.get('pm2_5'),
                    'pm10': components.get('pm10'),
                    'so2': components.get('so2'),
                    'no2': components.get('no2'),
                    'o3': components.get('o3'),
                    'co': components.get('co')
                })

            if days > 1:
                df_temp = pd.DataFrame(temp_data)
                df_temp['date'] = pd.to_datetime(df_temp['datetime']).dt.normalize()
                df_grouped = df_temp.groupby('date').agg({
                    'pm2_5': 'mean',
                    'pm10': 'mean',
                    'so2': 'mean',
                    'no2': 'mean',
                    'o3': 'mean',
                    'co': 'mean'
                }).reset_index()
                df_grouped['station'] = station['name']
                df_grouped['lat'] = station['lat']
                df_grouped['lon'] = station['lon']
                df_grouped['timeframe_days'] = days
                df_grouped = df_grouped.rename(columns={'date': 'datetime'})
                for _, row in df_grouped.iterrows():
                    all_data.append(row.to_dict())
            else:
                for item in temp_data:
                    item['timeframe_days'] = days
                all_data.extend(temp_data)
    return pd.DataFrame(all_data)

def fetch_current_station_data(api_key, stations):
    """Fetch current air pollution and temperature for each station."""
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    now_bangkok = datetime.now(bangkok_tz)
    current_month = now_bangkok.month

    all_data = []
    for station in stations:
        pollution_url = (
            f"http://api.openweathermap.org/data/2.5/air_pollution?"
            f"lat={station['lat']}&lon={station['lon']}&appid={api_key}"
        )
        pollution_response = requests.get(pollution_url)
        pollution_data = pollution_response.json()
        if 'list' not in pollution_data or not pollution_data['list']:
            print(f"No pollution data for station {station['name']}")
            continue
        pollution_entry = pollution_data['list'][0]
        dt = pd.to_datetime(pollution_entry['dt'], unit='s')
        components = pollution_entry.get('components', {})

        weather_url = (
            f"http://api.openweathermap.org/data/2.5/weather?"
            f"lat={station['lat']}&lon={station['lon']}&appid={api_key}&units=metric"
        )
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        temp = weather_data.get('main', {}).get('temp')
        if temp is None:
            print(f"No temperature data for {station['name']}, using default.")
            temp = 25

        season = map_season(current_month)

        record = {
            'datetime': dt.isoformat(),
            'station': station['name'],
            'lat': station['lat'],
            'lon': station['lon'],
            'pm2_5': components.get('pm2_5'),
            'pm10': components.get('pm10'),
            'so2': components.get('so2'),
            'no2': components.get('no2'),
            'o3': components.get('o3'),
            'co': components.get('co'),
            'temp': temp,
            'season': season
        }
        all_data.append(record)
    return pd.DataFrame(all_data)

# --------------------------------------------------------------------
# 4. Routes for Data Viewing
# --------------------------------------------------------------------
@app.route("/")
def home():
    data = fetch_data(api_key, stations)
    return render_template("home.html", data=data.to_dict(orient='records'), stations=stations)

@app.route("/fetch_table_data")
def fetch_table_data():
    data = fetch_data(api_key, stations)
    data_dict = data.to_dict(orient='records')
    sorted_data = sorted(data_dict, key=lambda x: (x.get('pm2_5') or 0), reverse=True)
    return jsonify(sorted_data)

@app.route("/pm25-details")
def pm25_details():
    df_pm25 = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    pm25_data = df_pm25.to_dict(orient="records")
    return render_template("pm25-details.html", pm25_data=pm25_data, stations=stations)

@app.route("/pm10-details")
def pm10_details():
    df_pm10 = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    pm10_data = df_pm10.to_dict(orient="records")
    return render_template("pm10-details.html", pm10_data=pm10_data, stations=stations)

@app.route("/so2-details")
def so2_details():
    df_so2 = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    so2_data = df_so2.to_dict(orient="records")
    return render_template("so2-details.html", so2_data=so2_data, stations=stations)

@app.route("/no2-details")
def no2_details():
    df_no2 = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    no2_data = df_no2.to_dict(orient="records")
    return render_template("no2-details.html", no2_data=no2_data, stations=stations)

@app.route("/o3-details")
def o3_details():
    df_o3 = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    o3_data = df_o3.to_dict(orient="records")
    return render_template("o3-details.html", o3_data=o3_data, stations=stations)

@app.route("/co-details")
def co_details():
    df_co = fetch_air_pollution_data(api_key, stations, days_list=[1, 7, 30])
    co_data = df_co.to_dict(orient="records")
    return render_template("co-details.html", co_data=co_data, stations=stations)

@app.route('/pm25-error')
def pm25_error():
    return render_template('error-page.html')


# --------------------------------------------------------------------
# 5. Simulation & Current Data Endpoints
# --------------------------------------------------------------------
current_stations = [
    {'name': 'Ratchathewi Station', 'lat': 13.7563, 'lon': 100.5018},
    {'name': 'Pathum Wan Station Station', 'lat': 13.7367, 'lon': 100.5231},
    {'name': 'Ladkrabang Station', 'lat': 13.7291, 'lon': 100.7750},
    {'name': 'Bang Na Station', 'lat': 13.6796, 'lon': 100.6067},
    {'name': 'Bang Khae Station', 'lat': 13.7083, 'lon': 100.3728},
    {'name': 'Taling Chan Station', 'lat': 13.7898, 'lon': 100.4486},
    {'name': 'Bang Sue Station', 'lat': 13.8225, 'lon': 100.5147}
]

@app.route("/fetch_current_data")
def fetch_current_data():
    data = fetch_current_station_data(api_key, current_stations)
    return jsonify(data.to_dict(orient='records'))

@app.route("/simulation")
def simulation():
    bangkok_tz = pytz.timezone('Asia/Bangkok')
    current_month = datetime.now(bangkok_tz).month
    default_season = map_season(current_month)
    return render_template("simulation.html", default_season=default_season)

# --------------------------------------------------------------------
# 6. Single Prediction Endpoint (/predict)
# --------------------------------------------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    print("Received data:", data)

    # Extract raw input values
    pm10 = data.get('pm10')
    so2 = data.get('so2')
    no2 = data.get('no2')
    temp = data.get('temp')
    o3 = data.get('o3')
    co = data.get('co')
    population_density = data.get('population_density')
    factory_area = data.get('factory_area')

    # Process season flags (binary values)
    season_cool = 1 if data.get('season_cool') else 0
    season_hot = 1 if data.get('season_hot') else 0
    season_rainy = 1 if data.get('season_rainy') else 0

    # Build a DataFrame with the log-transformed values and expected column names.
    input_dict = {
        'temp': [temp],
        'population_density': [population_density],
        'factory_area': [factory_area],
        'season_Cool Season': [season_cool],
        'season_Hot Season': [season_hot],
        'season_Rainy Season': [season_rainy],
        'pm10_log': [np.log1p(pm10)],
        'so2_log': [np.log1p(so2)],
        'no2_log': [np.log1p(no2)],
        'co_log': [np.log1p(co)],
        'o3_log': [np.log1p(o3)]
    }
    sample_df = pd.DataFrame(input_dict)
    # Reorder columns to match the expected order
    sample_df = sample_df[log_col_order]
    print("Input DataFrame after reordering:", sample_df)

    # Scale and predict
    sample_df_scaled = scaler.transform(sample_df)
    print("Scaled features:", sample_df_scaled)
    y_pred = model.predict(sample_df_scaled)
    print("Prediction:", y_pred[0])
    return jsonify({"prediction": float(y_pred[0])})

# --------------------------------------------------------------------
# 7. Multi-step Forecasting Prediction Endpoint (/prediction)
# --------------------------------------------------------------------
@app.route("/prediction", methods=["GET", "POST"])
def prediction():
    print("Here1")
    station_name = ""
    daily_predictions = {}    # For storing predictions by day
    table_data = []           # Detailed row-by-row forecasts
    summary_predictions = []  # Daily average predictions

    if request.method == "POST":
        selected_station = request.form.get("station")
        station_info = next((s for s in stations_for_prediction if s["name"] == selected_station), None)
        if not station_info:
            print("No station found for:", selected_station)
            return render_template("prediction.html", predictions=summary_predictions, table_data=table_data, station_name=station_name)

        lat = station_info["lat"]
        lon = station_info["lon"]
        population_density = station_info["population_density"]
        factory_area = station_info["factory_area"]

        weather_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        weather_response = requests.get(weather_url)
        weather_data = weather_response.json()
        print("Weather API response keys:", list(weather_data.keys()))
        if "list" not in weather_data:
            print("No weather data available.")
            return render_template("prediction.html", predictions=summary_predictions, table_data=table_data, station_name=station_name)

        weather_list = weather_data.get("list", [])
        weather_df = pd.DataFrame(weather_list)
        weather_df["datetime"] = pd.to_datetime(weather_df["dt"], unit="s")
        weather_df = weather_df.rename(columns={"main": "main_data"})
        weather_df = pd.concat([weather_df.drop(["main_data"], axis=1), weather_df["main_data"].apply(pd.Series)], axis=1)

        pollution_url = f"http://api.openweathermap.org/data/2.5/air_pollution/forecast?lat={lat}&lon={lon}&appid={api_key}"
        pollution_response = requests.get(pollution_url)
        pollution_data = pollution_response.json()
        print("Pollution API response keys:", list(pollution_data.keys()))
        pollution_list = pollution_data.get("list", [])
        pollution_df = pd.DataFrame(pollution_list)
        if pollution_df.empty:
            print("Pollution DataFrame is empty!")
            return render_template("prediction.html", predictions=summary_predictions, table_data=table_data, station_name=station_name)
        pollution_df["datetime"] = pd.to_datetime(pollution_df["dt"], unit="s")
        pollution_df = pollution_df.rename(columns={"components": "components_data"})
        pollution_df = pd.concat([pollution_df.drop(["components_data"], axis=1), pollution_df["components_data"].apply(pd.Series)], axis=1)

        merged_df = pd.merge_asof(
            weather_df.sort_values("datetime"),
            pollution_df.sort_values("datetime"),
            on="datetime",
            direction="nearest",
            tolerance=pd.Timedelta("1H")
        )
        required_cols = ["temp", "pm10", "so2", "no2", "o3", "co"]
        merged_df = merged_df.dropna(subset=required_cols)
        merged_df["date"] = merged_df["datetime"].dt.date

        today = datetime.now().date()
        future_dates = sorted([d for d in merged_df["date"].unique() if d > today])[:4]
        df_future = merged_df[merged_df["date"].isin(future_dates)]
        print("Future dates selected:", future_dates)

        for idx, row in df_future.iterrows():
            dt = row["datetime"]
            temp_val = row["temp"]
            pm10_val = row["pm10"]
            so2_val = row["so2"]
            no2_val = row["no2"]
            o3_val = row["o3"]
            co_val = row["co"]

            season_full = map_season(dt.month)
            if season_full == "Cool Season":
                display_season = "Cool"
            elif season_full == "Hot Season":
                display_season = "Hot"
            elif season_full == "Rainy Season":
                display_season = "Rainy"
            else:
                display_season = ""

            # Build a DataFrame row using the expected feature names and log transforms.
            row_dict = {
                'temp': [temp_val],
                'population_density': [population_density],
                'factory_area': [factory_area],
                'season_Cool Season': [1 if display_season == "Cool" else 0],
                'season_Hot Season': [1 if display_season == "Hot" else 0],
                'season_Rainy Season': [1 if display_season == "Rainy" else 0],
                'pm10_log': [np.log1p(pm10_val)],
                'so2_log': [np.log1p(so2_val)],
                'no2_log': [np.log1p(no2_val)],
                'co_log': [np.log1p(co_val)],
                'o3_log': [np.log1p(o3_val)]
            }
            df_features = pd.DataFrame(row_dict)
            df_features = df_features[log_col_order]
            features_scaled = scaler.transform(df_features)
            print(features_scaled)
            pred = model.predict(features_scaled)
            print(pred)
            pm25_pred = pred[0]
            print("Row Prediction:", pm25_pred)

            table_data.append({
                "day": dt.strftime("%Y-%m-%d"),
                "time": dt.strftime("%H:%M"),
                "temperature": temp_val,
                "pm10": pm10_val,
                "so2": so2_val,
                "no2": no2_val,
                "o3": o3_val,
                "co": co_val,
                "pm25": pm25_pred,
                "population_density": population_density,
                "factory_area": factory_area,
                "season": display_season
            })

            date_str = dt.strftime("%Y-%m-%d")
            if date_str not in daily_predictions:
                daily_predictions[date_str] = []
            daily_predictions[date_str].append(pm25_pred)

        for d in future_dates:
            d_str = d.strftime("%Y-%m-%d")
            if d_str in daily_predictions:
                avg_pm25 = np.mean(daily_predictions[d_str])
                summary_predictions.append({"day": d_str, "pm25": avg_pm25})
            else:
                summary_predictions.append({"day": d_str, "pm25": None})
        print("Summary predictions (daily averages):", summary_predictions)
        station_name = station_info["name"]

    return render_template("prediction.html", 
                           predictions=summary_predictions, 
                           table_data=table_data,
                           station_name=station_name)

# --------------------------------------------------------------------
# 8. Main Runner
# --------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

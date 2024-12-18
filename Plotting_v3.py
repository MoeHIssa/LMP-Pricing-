import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import certifi

# NOAA CDO API token
API_TOKEN = "HydjjAeoyFkmgTiQlUAmQCRnLqapLecO"

def fetch_with_retries(url, headers, params, retries=5, backoff_factor=2):
    """
    Fetch data from the API with retry logic.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params, verify=certifi.where())
            if response.status_code == 200:
                return response.json()
            elif response.status_code in {502, 503, 429}:  # Handle server and rate limit errors
                print(f"Error {response.status_code}: Retrying in {backoff_factor ** attempt} seconds...")
                time.sleep(backoff_factor ** attempt)
            else:
                response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}. Retrying in {backoff_factor ** attempt} seconds...")
            time.sleep(backoff_factor ** attempt)
    print("Max retries reached. Exiting.")
    return None

def fetch_cdo_historical_data(dataset_id, location_id, start_date, end_date):
    """
    Fetch historical daily weather data for a given time range.
    """
    base_url = "https://www.ncei.noaa.gov/cdo-web/api/v2/data"
    headers = {"token": API_TOKEN}
    params = {
        "datasetid": dataset_id,
        "locationid": location_id,
        "startdate": start_date,
        "enddate": end_date,
        "datatypeid": ["TMAX", "TMIN", "PRCP", "AWND", "RHUM"],
        "units": "metric",
        "limit": 1000
    }
    return fetch_with_retries(base_url, headers, params)

def process_data(historical_data):
    """
    Process raw data into a structured DataFrame with unit conversions.
    """
    df = pd.DataFrame(historical_data)
    if df.empty:
        print("No data retrieved.")
        return pd.DataFrame(), pd.DataFrame()

    # Convert dates
    df["date"] = pd.to_datetime(df["date"])

    # Convert units
    if "TMAX" in df["datatype"].unique():
        df.loc[df["datatype"] == "TMAX", "value"] = (df["value"] * 9/5) + 32  # Celsius to Fahrenheit
    if "TMIN" in df["datatype"].unique():
        df.loc[df["datatype"] == "TMIN", "value"] = (df["value"] * 9/5) + 32
    if "PRCP" in df["datatype"].unique():
        df.loc[df["datatype"] == "PRCP", "value"] = df["value"] * 0.03937  # mm to inches
    if "AWND" in df["datatype"].unique():
        df.loc[df["datatype"] == "AWND", "value"] = df["value"] * 2.23694  # m/s to mph

    # Aggregate data for station-level output
    station_data = df.pivot_table(index=["station", "date"], columns="datatype", values="value").reset_index()

    # Aggregate data for state-level output
    statewide_data = df.groupby(["date", "datatype"], as_index=False).agg({"value": "mean"})
    statewide_data = statewide_data.pivot(index="date", columns="datatype", values="value").reset_index()

    return station_data, statewide_data

# Fetch and process data one month at a time
location_id = "FIPS:06"  # California
dataset_id = "GHCND"
start_dates = pd.date_range("2023-01-01", "2024-11-30", freq="MS").strftime("%Y-%m-%d").tolist()
end_dates = (pd.date_range("2023-02-01", "2024-12-01", freq="MS") - timedelta(days=1)).strftime("%Y-%m-%d").tolist()

all_station_data = []
all_statewide_data = []

for start_date, end_date in zip(start_dates, end_dates):
    print(f"Fetching data for {start_date} to {end_date}...")
    chunk_data = fetch_cdo_historical_data(dataset_id, location_id, start_date, end_date)
    
    if chunk_data and "results" in chunk_data and chunk_data["results"]:
        station_data, statewide_data = process_data(chunk_data["results"])
        all_station_data.append(station_data)
        all_statewide_data.append(statewide_data)
    else:
        print(f"No data retrieved for {start_date} to {end_date}. Skipping...")

# Combine all monthly data into final DataFrames
if all_station_data:
    combined_station_data = pd.concat(all_station_data, ignore_index=True)
    station_output_file = "california_station_data_2023_2024.xlsx"
    with pd.ExcelWriter(station_output_file, engine="xlsxwriter") as writer:
        combined_station_data.to_excel(writer, index=False, sheet_name="Station Data")
    print(f"Station-level data saved to {station_output_file}")

if all_statewide_data:
    combined_statewide_data = pd.concat(all_statewide_data, ignore_index=True)
    statewide_output_file = "california_statewide_data_2023_2024.xlsx"
    with pd.ExcelWriter(statewide_output_file, engine="xlsxwriter") as writer:
        combined_statewide_data.to_excel(writer, index=False, sheet_name="Statewide Data")
    print(f"Statewide averaged data saved to {statewide_output_file}")

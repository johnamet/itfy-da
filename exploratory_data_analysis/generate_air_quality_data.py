"""Generates the synthetic Accra air-quality dataset for Topic 22.

Seeds real, discoverable patterns rather than pure noise:
  - station-type pollution gradient (Roadside > Industrial > Residential > Background)
  - a Dec-Feb Harmattan bump in particulates (PM2.5/PM10), not NO2
  - wind speed inversely related to PM (dispersion)
  - a weekday/weekend NO2 gap (traffic-linked)
  - two anomaly events: a 3-day single-station spike, and a 2-day citywide dust event
  - light, realistic missingness (short sensor-outage windows, pollutant columns only)

Run: python generate_air_quality_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent

STATIONS = [
    ("STN01", "Circle Interchange",       "Circle",              "Roadside"),
    ("STN02", "Kaneshie Market",          "Kaneshie",            "Roadside"),
    ("STN03", "Tema Motorway Roundabout", "Tema",                "Roadside"),
    ("STN04", "Osu Residential",          "Osu",                 "Residential"),
    ("STN05", "Dansoman Estate",          "Dansoman",            "Residential"),
    ("STN06", "East Legon Hills",         "East Legon",          "Residential"),
    ("STN07", "Tema Industrial Area",     "Tema Industrial Area", "Industrial"),
    ("STN08", "Achimota Industrial Zone", "Achimota",            "Industrial"),
    ("STN09", "Aburi Background Site",    "Aburi",               "Background"),
]

# A disjoint set of stations for the assignment - same underlying physics,
# different neighbourhoods and a different RNG draw, so the figures are
# genuinely new rather than memorised from the lesson.
ASSIGNMENT_STATIONS = [
    ("ASG01", "Madina Market Junction", "Madina",  "Roadside"),
    ("ASG02", "Spintex Road",           "Spintex", "Roadside"),
    ("ASG03", "Teshie Residential",     "Teshie",  "Residential"),
    ("ASG04", "Abossey Okai Workshops", "Abossey Okai", "Industrial"),
    ("ASG05", "Legon Botanical Site",   "Legon",   "Background"),
]

# Annual-mean PM2.5 baseline (ug/m3) by station type - realistic magnitudes for Accra,
# well above the WHO annual guideline of 5 ug/m3.
PM25_BASELINE = {"Roadside": 55.0, "Industrial": 40.0, "Residential": 28.0, "Background": 15.0}
PM10_RATIO = 1.8      # PM10 is consistently ~1.8x PM2.5 in Accra (high dust contribution)
NO2_BASELINE = {"Roadside": 38.0, "Industrial": 30.0, "Residential": 18.0, "Background": 9.0}

DATES = pd.date_range("2023-01-01", "2023-12-31", freq="D")


def harmattan_factor(day_of_year):
    """Smooth seasonal multiplier for particulates, peaking mid-January."""
    angle = 2 * np.pi * (day_of_year - 15) / 365.0
    return 1.0 + 0.65 * np.exp(-2.5 * (1 - np.cos(angle)))


def build_readings(station_list, rng, single_station_anomaly, citywide_anomaly, outages):
    rows = []
    for station_id, _, _, station_type in station_list:
        pm25_base = PM25_BASELINE[station_type]
        no2_base = NO2_BASELINE[station_type]

        wind = np.clip(rng.lognormal(mean=np.log(9.0), sigma=0.35, size=len(DATES)), 2, 35)
        temperature = 27.5 + 3.0 * np.cos(2 * np.pi * (DATES.dayofyear - 60) / 365.0) \
            + rng.normal(0, 1.1, len(DATES))
        humidity = 72 - 10 * np.cos(2 * np.pi * (DATES.dayofyear - 60) / 365.0) \
            - 14 * np.exp(-2.5 * (1 - np.cos(2 * np.pi * (DATES.dayofyear - 15) / 365.0))) \
            + rng.normal(0, 4, len(DATES))
        humidity = np.clip(humidity, 20, 98)

        season = harmattan_factor(DATES.dayofyear.values)
        wind_effect = 1.0 - 0.35 * (wind - 9.0) / 9.0
        pm25 = pm25_base * season * np.clip(wind_effect, 0.5, 1.6) \
            * rng.normal(1.0, 0.12, len(DATES))
        pm25 = np.clip(pm25, 3, None)
        pm10 = pm25 * PM10_RATIO * rng.normal(1.0, 0.05, len(DATES))

        is_weekend = np.asarray(DATES.dayofweek.isin([5, 6]))
        no2 = no2_base * np.where(is_weekend, 0.75, 1.0) * rng.normal(1.0, 0.10, len(DATES))
        no2 = np.clip(no2, 2, None)

        for i, date in enumerate(DATES):
            rows.append({
                "station_id": station_id, "date": date.strftime("%Y-%m-%d"),
                "pm2_5": round(float(pm25[i]), 1), "pm10": round(float(pm10[i]), 1),
                "no2": round(float(no2[i]), 1),
                "temperature_c": round(float(temperature[i]), 1),
                "humidity_pct": round(float(humidity[i]), 1),
                "wind_speed_kmh": round(float(wind[i]), 1),
            })

    df = pd.DataFrame(rows)

    # --- A single-station spike (e.g. an industrial incident) ---------------
    station_id, start, end, pm25_mult, pm10_mult = single_station_anomaly
    mask = (df["station_id"] == station_id) & df["date"].between(start, end)
    df.loc[mask, "pm2_5"] = (df.loc[mask, "pm2_5"] * pm25_mult).round(1)
    df.loc[mask, "pm10"] = (df.loc[mask, "pm10"] * pm10_mult).round(1)

    # --- A citywide event, outside the Harmattan window ----------------------
    start, end, pm25_mult, pm10_mult = citywide_anomaly
    mask = df["date"].between(start, end)
    df.loc[mask, "pm2_5"] = (df.loc[mask, "pm2_5"] * pm25_mult).round(1)
    df.loc[mask, "pm10"] = (df.loc[mask, "pm10"] * pm10_mult).round(1)

    # --- Light, realistic missingness: short sensor-outage windows ----------
    for station_id, start, end in outages:
        mask = (df["station_id"] == station_id) & df["date"].between(start, end)
        df.loc[mask, ["pm2_5", "pm10", "no2"]] = np.nan

    return df.sort_values(["date", "station_id"]).reset_index(drop=True)


def build_stations(station_list):
    return pd.DataFrame(station_list, columns=["station_id", "station_name", "neighborhood", "station_type"])


if __name__ == "__main__":
    data_dir = HERE / "data"

    stations = build_stations(STATIONS)
    readings = build_readings(
        STATIONS, np.random.default_rng(22),
        single_station_anomaly=("STN07", "2023-06-10", "2023-06-12", 4.6, 4.2),
        citywide_anomaly=("2023-03-22", "2023-03-23", 3.1, 2.8),
        outages=[("STN02", "2023-04-05", "2023-04-07"),
                 ("STN05", "2023-08-19", "2023-08-19"),
                 ("STN09", "2023-10-02", "2023-10-04")],
    )
    stations.to_csv(data_dir / "air_quality_stations.csv", index=False)
    readings.to_csv(data_dir / "air_quality_readings.csv", index=False)
    print(f"wrote air_quality_stations.csv ({len(stations)} rows)")
    print(f"wrote air_quality_readings.csv ({len(readings)} rows)")

    # Assignment variant: disjoint stations, different seed, different anomaly
    # dates/station - same underlying physics, genuinely new figures.
    asg_stations = build_stations(ASSIGNMENT_STATIONS)
    asg_readings = build_readings(
        ASSIGNMENT_STATIONS, np.random.default_rng(220),
        single_station_anomaly=("ASG04", "2023-09-05", "2023-09-07", 4.3, 4.0),
        citywide_anomaly=("2023-07-14", "2023-07-15", 2.9, 2.6),
        outages=[("ASG02", "2023-02-10", "2023-02-11"),
                 ("ASG05", "2023-11-20", "2023-11-22")],
    )
    asg_stations.to_csv(data_dir / "air_quality_stations_assignment.csv", index=False)
    asg_readings.to_csv(data_dir / "air_quality_readings_assignment.csv", index=False)
    print(f"wrote air_quality_stations_assignment.csv ({len(asg_stations)} rows)")
    print(f"wrote air_quality_readings_assignment.csv ({len(asg_readings)} rows)")

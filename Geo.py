import pandas as pd
import time
from geopy.geocoders import ArcGIS
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

df = pd.read_csv("power4_attributes(Sheet1).csv")

city_cols = ["City 1", "City 2", "City 3"]

geolocator = ArcGIS(timeout=10)

cache = {}

def get_lat_lon(city):
    if pd.isna(city) or str(city).strip() == "":
        return None, None

    city = str(city).strip()

    if city in cache:
        return cache[city]

    try:
        location = geolocator.geocode(city)

        if location:
            result = (location.latitude, location.longitude)
            print(f"Found: {city} -> {result}")
        else:
            result = (None, None)
            print(f"Not found: {city}")

    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"Temporary error with {city}: {e}")
        result = (None, None)

    except Exception as e:
        print(f"Error with {city}: {e}")
        result = (None, None)

    cache[city] = result
    time.sleep(0.2)
    return result


for col in city_cols:
    df[[f"{col}_lat", f"{col}_lon"]] = df[col].apply(
        lambda x: pd.Series(get_lat_lon(x))
    )

df.to_csv("geocoded_power4.csv", index=False)

print("Done! Saved as geocoded_power4.csv")
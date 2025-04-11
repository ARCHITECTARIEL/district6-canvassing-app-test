import streamlit as st
import json
import requests
import pandas as pd

@st.cache_data
def load_addresses():
    # Try addresses.json from GitHub
    github_url = "https://raw.githubusercontent.com/ARCHITECTARIEL/district6-canvassing-app-test/main/addresses.json"
    try:
        response = requests.get(github_url)
        if response.status_code == 200:
            address_data = response.json()
            st.sidebar.success(f"Loaded {len(address_data)} addresses from addresses.json")
            process_address_data(address_data)
            return address_data
        else:
            st.sidebar.warning("Couldn’t find addresses.json on GitHub")
    except Exception as e:
        st.sidebar.warning(f"Error with addresses.json: {e}")

    # Try Voting Precincts 2022.geojson from GitHub
    github_url = "https://raw.githubusercontent.com/ARCHITECTARIEL/district6-canvassing-app-test/main/Voting%20Precincts%202022.geojson"
    try:
        response = requests.get(github_url)
        if response.status_code == 200:
            geojson_data = response.json()
            address_data = []
            for feature in geojson_data.get("features", []):
                props = feature.get("properties", {})
                geometry = feature.get("geometry", {})
                lat, lon = None, None
                coords = geometry.get("coordinates", [])
                if geometry.get("type") == "Point":
                    lon, lat = coords
                elif geometry.get("type") == "Polygon" and coords:
                    x_sum, y_sum, count = 0, 0, 0
                    for ring in coords:
                        for x, y in ring:
                            x_sum += x
                            y_sum += y
                            count += 1
                    if count > 0:
                        lon = x_sum / count
                        lat = y_sum / count
                address = {
                    "PARCEL_NUMBER": props.get("PARCEL_NUMBER", f"GEO-{len(address_data)}"),
                    "OWNER1": props.get("OWNER1", "Unknown"),
                    "SITE_ADDRESS": props.get("SITE_ADDRESS", "Unknown"),
                    "SITE_CITYZIP": props.get("SITE_CITYZIP", "ST PETERSBURG, FL 33705"),
                    "PROPERTY_USE": props.get("PROPERTY_USE", "Residential"),
                    "STR_NUM": props.get("STR_NUM", 0),
                    "STR_NAME": props.get("STR_NAME", "Unknown"),
                    "STR_ZIP": props.get("STR_ZIP", "33705"),
                    "PRECINCT": str(props.get("PRECINCT", "130")),
                    "LAT": lat if lat else 27.773056,
                    "LON": lon if lon else -82.639999,
                    "SECTION": props.get("SECTION", "North")
                }
                address_data.append(address)
            st.sidebar.success(f"Loaded {len(address_data)} addresses from GeoJSON")
            process_address_data(address_data)
            return address_data
        else:
            st.sidebar.warning("Couldn’t find Voting Precincts 2022.geojson")
    except Exception as e:
        st.sidebar.warning(f"Error with GeoJSON: {e}")

    # File uploader for backup
    st.sidebar.subheader("Upload Address File")
    uploaded_file = st.sidebar.file_uploader("Choose JSON or GeoJSON", type=["json", "geojson"])
    if uploaded_file:
        try:
            content = uploaded_file.read().decode("utf-8")
            if uploaded_file.name.endswith(".geojson"):
                geojson_data = json.loads(content)
                address_data = []
                for feature in geojson_data.get("features", []):
                    props = feature.get("properties", {})
                    geometry = feature.get("geometry", {})
                    lat, lon = None, None
                    coords = geometry.get("coordinates", [])
                    if geometry.get("type") == "Point":
                        lon, lat = coords
                    elif geometry.get("type") == "Polygon" and coords:
                        x_sum, y_sum, count = 0, 0, 0
                        for ring in coords:
                            for x, y in ring:
                                x_sum += x
                                y_sum += y
                                count += 1
                        if count > 0:
                            lon = x_sum / count
                            lat = y_sum / count
                    address = {
                        "PARCEL_NUMBER": props.get("PARCEL_NUMBER", f"GEO-{len(address_data)}"),
                        "OWNER1": props.get("OWNER1", "Unknown"),
                        "SITE_ADDRESS": props.get("SITE_ADDRESS", "Unknown"),
                        "SITE_CITYZIP": props.get("SITE_CITYZIP", "ST PETERSBURG, FL 33705"),
                        "PROPERTY_USE": props.get("PROPERTY_USE", "Residential"),
                        "STR_NUM": props.get("STR_NUM", 0),
                        "STR_NAME": props.get("STR_NAME", "Unknown"),
                        "STR_ZIP": props.get("STR_ZIP", "33705"),
                        "PRECINCT": str(props.get("PRECINCT", "130")),
                        "LAT": lat if lat else 27.773056,
                        "LON": lon if lon else -82.639999,
                        "SECTION": props.get("SECTION", "North")
                    }
                    address_data.append(address)
            else:
                address_data = json.loads(content)
            st.sidebar.success(f"Loaded {len(address_data)} addresses from uploaded file")
            process_address_data(address_data)
            return address_data
        except Exception as e:
            st.sidebar.error(f"Error with uploaded file: {e}")

    # Fall back to sample data
    st.sidebar.error("No files loaded. Using sample data.")
    return generate_sample_addresses()
    

import streamlit as st
import pandas as pd
import json
import os
import re
import requests
from urllib.parse import quote
from collections import defaultdict

# Set page configuration
st.set_page_config(
    page_title="District 6 Canvassing App",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'volunteer_name' not in st.session_state:
    st.session_state.volunteer_name = ""
if 'selected_precinct' not in st.session_state:
    st.session_state.selected_precinct = None
if 'visited_addresses' not in st.session_state:
    st.session_state.visited_addresses = set()
if 'interaction_notes' not in st.session_state:
    st.session_state.interaction_notes = {}
if 'address_data' not in st.session_state:
    st.session_state.address_data = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'search_suggestions' not in st.session_state:
    st.session_state.search_suggestions = []
if 'precinct_addresses' not in st.session_state:
    st.session_state.precinct_addresses = {}
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'cluster_view' not in st.session_state:
    st.session_state.cluster_view = True
if 'selected_cluster' not in st.session_state:
    st.session_state.selected_cluster = None
if 'support_levels' not in st.session_state:
    st.session_state.support_levels = {}
if 'donations' not in st.session_state:
    st.session_state.donations = {}
if 'current_page' not in st.session_state:
    st.session_state.current_page = "home"
if 'contact_address' not in st.session_state:
    st.session_state.contact_address = None
if 'json_load_error' not in st.session_state:
    st.session_state.json_load_error = None
if 'geographic_section' not in st.session_state:
    st.session_state.geographic_section = "All"
if 'user_location' not in st.session_state:
    st.session_state.user_location = None

# Function to navigate between pages
def navigate_to(page, address=None):
    if address is not None:
        st.session_state.contact_address = address
    st.session_state.current_page = page
    # Use st.rerun() instead of st.experimental_rerun() which is deprecated
    st.rerun()

# Sidebar for navigation
st.sidebar.title("District 6 Canvassing")

# Real District 6 precinct data - removed strategy tags
def get_district6_precincts():
    return [
        {"id": "106", "name": "Precinct 106", "total_addresses": 760, "turnout": "88.55%", "zip_codes": ["33701", "33705"], "section": "North"},
        {"id": "108", "name": "Precinct 108", "total_addresses": 2773, "turnout": "81.79%", "zip_codes": ["33701", "33705"], "section": "North"},
        {"id": "109", "name": "Precinct 109", "total_addresses": 2151, "turnout": "77.59%", "zip_codes": ["33701", "33705"], "section": "East"},
        {"id": "116", "name": "Precinct 116", "total_addresses": 1511, "turnout": "67.97%", "zip_codes": ["33701", "33705"], "section": "East"},
        {"id": "117", "name": "Precinct 117", "total_addresses": 1105, "turnout": "62.53%", "zip_codes": ["33701", "33705"], "section": "South"},
        {"id": "118", "name": "Precinct 118", "total_addresses": 1175, "turnout": "85.36%", "zip_codes": ["33701", "33705"], "section": "South"},
        {"id": "119", "name": "Precinct 119", "total_addresses": 2684, "turnout": "65.31%", "zip_codes": ["33701", "33705"], "section": "West"},
        {"id": "121", "name": "Precinct 121", "total_addresses": 922, "turnout": "77.55%", "zip_codes": ["33701", "33705"], "section": "West"},
        {"id": "122", "name": "Precinct 122", "total_addresses": 258, "turnout": "87.60%", "zip_codes": ["33701", "33705"], "section": "North"},
        {"id": "123", "name": "Precinct 123", "total_addresses": 4627, "turnout": "85.35%", "zip_codes": ["33701", "33705"], "section": "East"},
        {"id": "125", "name": "Precinct 125", "total_addresses": 1301, "turnout": "79.94%", "zip_codes": ["33701", "33705"], "section": "South"},
        {"id": "126", "name": "Precinct 126", "total_addresses": 1958, "turnout": "77.07%", "zip_codes": ["33701", "33705"], "section": "West"},
        {"id": "130", "name": "Precinct 130", "total_addresses": 3764, "turnout": "86.16%", "zip_codes": ["33701", "33705"], "section": "North"}
    ]

# Generate sample addresses as fallback
def generate_sample_addresses():
    st.warning("Using generated sample addresses as fallback.")
    sample_data = []
    
    # Add Ariel's address to the sample data
    sample_data.append({
        "PARCEL_NUMBER": "ARIEL-RESIDENCE",
        "OWNER1": "FERNANDEZ, ARIEL",
        "OWNER2": "",
        "SITE_ADDRESS": "315 TAYLOR AVE S",
        "SITE_CITYZIP": "ST PETERSBURG, FL 33705",
        "SUBDIVISION": "DISTRICT 6",
        "MAILING_ADDRESS_1": "315 TAYLOR AVE S",
        "MAILING_CITY": "ST PETERSBURG",
        "MAILING_STATE": "FL",
        "MAILING_ZIP": "33705",
        "PROPERTY_USE": "Residential",
        "HX_YN": "Yes",
        "STR_NUM": 315,
        "STR_NAME": "TAYLOR",
        "STR_UNIT": "",
        "STR_ZIP": "33705",
        "PRECINCT": "106",  # Explicitly assign precinct
        "LAT": 27.773056,  # Add coordinates for map
        "LON": -82.639999,
        "SECTION": "North"  # Assign geographic section
    })
    
    # Generate additional sample addresses for each precinct
    precincts = get_district6_precincts()
    for precinct in precincts:
        precinct_id = precinct["id"]
        section = precinct["section"]
        
        # Generate a few apartment buildings/condos with multiple units
        for b in range(3):
            building_num = 100 + b * 100
            building_name = ["OAK TERRACE", "PALM HEIGHTS", "BAYVIEW TOWERS", "SUNSET CONDOS"][b % 4]
            street_name = ["MAIN", "OAK", "BEACH", "CENTRAL"][b % 4]
            zip_code = "33701" if b % 2 == 0 else "33705"
            
            # Base coordinates for this building
            base_lat = 27.773056 + (int(precinct_id) % 10) * 0.001
            base_lon = -82.639999 - (int(precinct_id) % 5) * 0.001
            
            # Generate multiple units in the same building
            for i in range(10):  # 10 units per building
                unit_num = i + 1
                
                # Small offset for each unit in the same building
                unit_lat = base_lat + i * 0.00005
                unit_lon = base_lon + i * 0.00005
                
                sample_data.append({
                    "PARCEL_NUMBER": f"SAMPLE-{precinct_id}-BLDG{b}-UNIT{unit_num}",
                    "OWNER1": f"RESIDENT {precinct_id}-{b}-{unit_num}",
                    "OWNER2": "FAMILY MEMBER" if i % 3 == 0 else "",
                    "SITE_ADDRESS": f"{building_num} {street_name} ST APT {unit_num}",
                    "SITE_CITYZIP": f"ST PETERSBURG, FL {zip_code}",
                    "PROPERTY_USE": "Residential",
                    "HX_YN": "Yes" if i % 2 == 0 else "No",
                    "STR_NUM": building_num,
                    "STR_NAME": street_name,
                    "STR_UNIT": f"APT {unit_num}",
                    "STR_ZIP": zip_code,
                    "PRECINCT": precinct_id,  # Explicitly assign precinct
                    "BUILDING_NAME": building_name,
                    "LAT": unit_lat,  # Add coordinates for map
                    "LON": unit_lon,
                    "SECTION": section  # Assign geographic section
                })
        
        # Generate some single-family homes
        for i in range(10):  # 10 single-family homes per precinct
            home_num = 200 + i * 10
            street_name = ["PINE", "MAPLE", "PALM", "OCEAN"][i % 4]
            zip_code = "33701" if i % 2 == 0 else "33705"
            
            # Coordinates for this home
            home_lat = 27.773056 + (int(precinct_id) % 10) * 0.001 + i * 0.0001
            home_lon = -82.639999 - (int(precinct_id) % 5) * 0.001 - i * 0.0001
            
            sample_data.append({
                "PARCEL_NUMBER": f"SAMPLE-{precinct_id}-HOME-{i}",
                "OWNER1": f"RESIDENT {precinct_id}-HOME-{i}",
                "OWNER2": "FAMILY MEMBER" if i % 3 == 0 else "",
                "SITE_ADDRESS": f"{home_num} {street_name} AVE",
                "SITE_CITYZIP": f"ST PETERSBURG, FL {zip_code}",
                "PROPERTY_USE": "Residential",
                "HX_YN": "Yes" if i % 2 == 0 else "No",
                "STR_NUM": home_num,
                "STR_NAME": street_name,
                "STR_UNIT": "",
                "STR_ZIP": zip_code,
                "PRECINCT": precinct_id,  # Explicitly assign precinct
                "LAT": home_lat,  # Add coordinates for map
                "LON": home_lon,
                "SECTION": section  # Assign geographic section
            })
        
        # Generate some businesses
        for i in range(5):  # 5 businesses per precinct
            business_num = 300 + i * 10
            street_name = ["COMMERCIAL", "BUSINESS", "MARKET", "OFFICE"][i % 4]
            zip_code = "33701" if i % 2 == 0 else "33705"
            
            # Coordinates for this business
            biz_lat = 27.773056 + (int(precinct_id) % 10) * 0.001 - i * 0.0001
            biz_lon = -82.639999 - (int(precinct_id) % 5) * 0.001 + i * 0.0001
            
            sample_data.append({
                "PARCEL_NUMBER": f"SAMPLE-{precinct_id}-BIZ-{i}",
                "OWNER1": f"BUSINESS {precinct_id}-BIZ-{i}",
                "OWNER2": "",
                "SITE_ADDRESS": f"{business_num} {street_name} BLVD",
                "SITE_CITYZIP": f"ST PETERSBURG, FL {zip_code}",
                "PROPERTY_USE": "Business",
                "HX_YN": "No",
                "STR_NUM": business_num,
                "STR_NAME": street_name,
                "STR_UNIT": "",
                "STR_ZIP": zip_code,
                "PRECINCT": precinct_id,  # Explicitly assign precinct
                "LAT": biz_lat,  # Add coordinates for map
                "LON": biz_lon,
                "SECTION": section  # Assign geographic section
            })
    
    return sample_data

# Function to fix JSON formatting issues
def fix_json_format(content):
    """Fix common JSON formatting issues"""
    try:
        # Check if the content is already valid JSON
        json.loads(content)
        return content
    except json.JSONDecodeError:
        # Fix common issues
        fixed_content = content
        
        # Ensure content starts with '[' and ends with ']'
        fixed_content = fixed_content.strip()
        if not fixed_content.startswith('['):
            fixed_content = '[' + fixed_content
        if not fixed_content.endswith(']'):
            fixed_content = fixed_content + ']'
        
        # Remove any problematic characters at the beginning
        if fixed_content[0] != '[':
            fixed_content = '[' + fixed_content[fixed_content.find('{'): fixed_content.rfind('}')+1] + ']'
        
        # Try to parse the fixed content
        try:
            json.loads(fixed_content)
            return fixed_content
        except json.JSONDecodeError:
            # If still invalid, return None
            return None

# Load addresses from local file or GitHub
@st.cache_data
def load_addresses():
    # File paths to try in order
    file_paths = [
        '/home/ubuntu/fixed_addresses.json',  # Our fixed version
        '/home/ubuntu/addresses.json',
        '/home/ubuntu/upload/addresses.json',
        '/home/ubuntu/upload/Advanced Search 4-11-2025 (1).json'
    ]
    
    # Try local files first
    for file_path in file_paths:
        try:
            st.sidebar.info(f"Attempting to load: {file_path}")
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Try to parse as is
                try:
                    address_data = json.loads(content)
                    st.sidebar.success(f"Successfully loaded {len(address_data)} addresses from {file_path}")
                    process_address_data(address_data)
                    return address_data
                except json.JSONDecodeError as e:
                    # Try to fix the JSON format
                    st.sidebar.warning(f"JSON parsing error: {str(e)}. Attempting to fix...")
                    fixed_content = fix_json_format(content)
                    if fixed_content:
                        try:
                            address_data = json.loads(fixed_content)
                            st.sidebar.success(f"Successfully fixed and loaded {len(address_data)} addresses from {file_path}")
                            process_address_data(address_data)
                            return address_data
                        except json.JSONDecodeError as e2:
                            st.sidebar.error(f"Could not fix JSON format: {str(e2)}")
                    else:
                        st.sidebar.error("Could not fix JSON format")
        except Exception as e:
            st.sidebar.warning(f"Could not load {file_path}: {str(e)}")
    
    # If local files fail, try GitHub
    try:
        # Try multiple possible filenames
        filenames = [
            "fixed_addresses.json",
            "addresses.json",
            "Advanced Search 4-11-2025 (1).json",
            "Advanced_Search_4-11-2025_(1).json"
        ]
        
        for filename in filenames:
            encoded_filename = quote(filename)
            github_url = f"https://raw.githubusercontent.com/ARCHITECTARIEL/district6-canvassing-app-test/main/{encoded_filename}"
            
            st.sidebar.info(f"Attempting to load from GitHub: {github_url}")
            
            # Fetch the file from GitHub
            response = requests.get(github_url)
            
            # Check if the request was successful
            if response.status_code == 200:
                content = response.text
                
                # Try to parse as is
                try:
                    address_data = json.loads(content)
                    st.sidebar.success(f"Successfully loaded {len(address_data)} addresses from GitHub")
                    process_address_data(address_data)
                    return address_data
                except json.JSONDecodeError as e:
                    # Try to fix the JSON format
                    st.sidebar.warning(f"JSON parsing error: {str(e)}. Attempting to fix...")
                    fixed_content = fix_json_format(content)
                    if fixed_content:
                        try:
                            address_data = json.loads(fixed_content)
                            st.sidebar.success(f"Successfully fixed and loaded {len(address_data)} addresses from GitHub")
                            process_address_data(address_data)
                            return address_data
                        except json.JSONDecodeError as e2:
                            st.sidebar.error(f"Could not fix JSON format: {str(e2)}")
                    else:
                        st.sidebar.error("Could not fix JSON format")
    except Exception as e:
        st.sidebar.error(f"Error loading addresses from GitHub: {str(e)}")
    
    # File upload option as last resort
    st.sidebar.warning("Could not load address data from files or GitHub. Please upload a file.")
    uploaded_file = st.sidebar.file_uploader("Upload address data (JSON format)", type=["json"])
    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode()
            
            # Try to parse as is
            try:
                address_data = json.loads(content)
                st.sidebar.success(f"Successfully loaded {len(address_data)} addresses from uploaded file")
                process_address_data(address_data)
                return address_data
            except json.JSONDecodeError as e:
                # Try to fix the JSON format
      
(Content truncated due to size limit. Use line ranges to read in chunks)

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
                st.sidebar.warning(f"JSON parsing error: {str(e)}. Attempting to fix...")
                fixed_content = fix_json_format(content)
                if fixed_content:
                    try:
                        address_data = json.loads(fixed_content)
                        st.sidebar.success(f"Successfully fixed and loaded {len(address_data)} addresses from uploaded file")
                        process_address_data(address_data)
                        return address_data
                    except json.JSONDecodeError as e2:
                        st.sidebar.error(f"Could not fix JSON format: {str(e2)}")
                        st.session_state.json_load_error = str(e2)
                else:
                    st.sidebar.error("Could not fix JSON format")
                    st.session_state.json_load_error = "Could not fix JSON format"
        except Exception as e:
            st.sidebar.error(f"Error processing uploaded file: {str(e)}")
            st.session_state.json_load_error = str(e)
    
    # If all else fails, use sample data
    st.sidebar.error("All attempts to load address data failed. Using sample data instead.")
    return generate_sample_addresses()

# Process address data
def process_address_data(address_data):
    # Add precinct information if not present
    for address in address_data:
        # Clean up property use to be either "Residential" or "Business"
        property_use = str(address.get('PROPERTY_USE', ''))
        if '0300' in property_use or 'Multi-Family' in property_use or 'Condo' in property_use or 'Apartment' in property_use:
            address['PROPERTY_USE'] = "Residential"
        elif '0100' in property_use or '0110' in property_use or 'Single Family' in property_use or 'Home' in property_use:
            address['PROPERTY_USE'] = "Residential"
        elif 'Commercial' in property_use or 'Business' in property_use or 'Office' in property_use or 'Retail' in property_use:
            address['PROPERTY_USE'] = "Business"
        else:
            # Default to residential if unclear
            address['PROPERTY_USE'] = "Residential"
        
        # Check if address already has precinct info
        if 'PRECINCT' not in address:
            # Assign precinct based on ZIP code
            zip_code = str(address.get('STR_ZIP', ''))
            
            # Simple assignment logic - in a real app, this would use geospatial data
            # For now, we'll assign based on a simple pattern
            if zip_code == '33705':
                # Distribute 33705 addresses across precincts
                street_num = int(address.get('STR_NUM', 0))
                if street_num < 200:
                    address['PRECINCT'] = '106'
                elif street_num < 400:
                    address['PRECINCT'] = '108'
                elif street_num < 600:
                    address['PRECINCT'] = '109'
                elif street_num < 800:
                    address['PRECINCT'] = '116'
                else:
                    address['PRECINCT'] = '117'
            elif zip_code == '33701':
                # Distribute 33701 addresses across precincts
                street_num = int(address.get('STR_NUM', 0))
                if street_num < 200:
                    address['PRECINCT'] = '118'
                elif street_num < 400:
                    address['PRECINCT'] = '119'
                elif street_num < 600:
                    address['PRECINCT'] = '121'
                elif street_num < 800:
                    address['PRECINCT'] = '122'
                else:
                    address['PRECINCT'] = '123'
            else:
                # Default precinct for other ZIP codes
                address['PRECINCT'] = '130'
            
            # Special case for Ariel's address
            if (address.get('STR_NUM') == 315 and 
                'TAYLOR' in str(address.get('STR_NAME', '')) and 
                address.get('STR_ZIP') == '33705'):
                address['PRECINCT'] = '106'
                address['OWNER1'] = 'FERNANDEZ, ARIEL'
        
        # Add building name if not present for multi-family properties
        if 'BUILDING_NAME' not in address:
            property_use = str(address.get('PROPERTY_USE', ''))
            if '0300' in property_use or 'Multi-Family' in property_use or 'Condo' in property_use or 'Apartment' in property_use:
                # Extract building name from address or create one
                street_num = str(address.get('STR_NUM', ''))
                street_name = str(address.get('STR_NAME', ''))
                if street_name:
                    address['BUILDING_NAME'] = f"{street_name.title()} {street_num} Condos"
                else:
                    address['BUILDING_NAME'] = f"Building {street_num}"
        
        # Add coordinates for map if not present
        if 'LAT' not in address or 'LON' not in address:
            # Generate a latitude and longitude near St. Petersburg, FL
            # This is just for demonstration - real app would use actual coordinates
            base_lat = 27.773056  # St. Petersburg latitude
            base_lon = -82.639999  # St. Petersburg longitude
            
            # Add small offsets based on street number and precinct to create a scatter effect
            street_num = float(address.get('STR_NUM', 0))
            precinct_id = str(address.get('PRECINCT', '106'))
            
            address['LAT'] = base_lat + (street_num % 100) * 0.0001 + (int(precinct_id) % 10) * 0.001
            address['LON'] = base_lon + (street_num % 50) * 0.0002 - (int(precinct_id) % 5) * 0.001
        
        # Add geographic section based on precinct
        if 'SECTION' not in address:
            precinct_id = str(address.get('PRECINCT', ''))
            precincts = get_district6_precincts()
            precinct_info = next((p for p in precincts if p['id'] == precinct_id), None)
            
            if precinct_info:
                address['SECTION'] = precinct_info['section']
            else:
                # Default to North if precinct not found
                address['SECTION'] = "North"
    
    # Make sure Ariel's address is included
    ariel_exists = False
    for address in address_data:
        owner1 = str(address.get('OWNER1', ''))
        if (address.get('STR_NUM') == 315 and 
            'TAYLOR' in str(address.get('STR_NAME', '')) and 
            address.get('STR_ZIP') == '33705'):
            ariel_exists = True
            # Make sure Ariel's address has coordinates
            if 'LAT' not in address or 'LON' not in address:
                address['LAT'] = 27.773056  # St. Petersburg latitude
                address['LON'] = -82.639999  # St. Petersburg longitude
            # Make sure Ariel's address has a section
            address['SECTION'] = "North"
            break
    
    # Add Ariel's address if not found
    if not ariel_exists:
        ariel_address = {
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
        }
        address_data.append(ariel_address)
        st.sidebar.success("Added Ariel Fernandez's address to the dataset")

# Simple function to group addresses by proximity without using sklearn
def simple_group_addresses(addresses):
    # Group by street name first
    street_groups = defaultdict(list)
    for address in addresses:
        street_name = str(address.get('STR_NAME', '')).upper()
        if street_name:
            street_groups[street_name].append(address)
    
    # For each street, group by building number ranges
    building_groups = []
    for street_name, street_addresses in street_groups.items():
        # Sort by building number
        sorted_addresses = sorted(street_addresses, key=lambda x: int(x.get('STR_NUM', 0)))
        
        # Group into chunks of nearby buildings
        chunk_size = 5  # Adjust as needed
        for i in range(0, len(sorted_addresses), chunk_size):
            chunk = sorted_addresses[i:i+chunk_size]
            if chunk:
                # Create a group name based on street and number range
                start_num = chunk[0].get('STR_NUM', 0)
                end_num = chunk[-1].get('STR_NUM', 0)
                group_name = f"{street_name} {start_num}-{end_num}"
                building_groups.append((group_name, chunk))
    
    return building_groups

# Load address data when the app starts
if not st.session_state.data_loaded:
    st.session_state.address_data = load_addresses()
    st.session_state.data_loaded = True

# Organize addresses by precinct
def organize_addresses_by_precinct():
    if 'precinct_addresses' not in st.session_state or not st.session_state.precinct_addresses:
        st.session_state.precinct_addresses = {}
        
        # Get all precincts
        precincts = get_district6_precincts()
        for precinct in precincts:
            precinct_id = precinct["id"]
            st.session_state.precinct_addresses[precinct_id] = []
        
        # Assign addresses to precincts
        for address in st.session_state.address_data:
            precinct_id = str(address.get('PRECINCT', ''))
            
            # If precinct is not specified or invalid, try to determine it
            if precinct_id not in st.session_state.precinct_addresses:
                # Simple assignment logic based on ZIP code
                zip_code = str(address.get('STR_ZIP', ''))
                if zip_code == '33705':
                    precinct_id = '106'  # Default for 33705
                elif zip_code == '33701':
                    precinct_id = '118'  # Default for 33701
                else:
                    precinct_id = '130'  # Default for other ZIP codes
            
            # Add address to the appropriate precinct
            if precinct_id in st.session_state.precinct_addresses:
                st.session_state.precinct_addresses[precinct_id].append(address)

# Group addresses by building/neighborhood
def group_addresses():
    if st.session_state.selected_precinct:
        precinct_id = st.session_state.selected_precinct
        addresses = st.session_state.precinct_addresses.get(precinct_id, [])
        
        # Dictionary to store buildings and their addresses
        buildings = defaultdict(list)
        
        # Group addresses by building
        for address in addresses:
            # For multi-unit buildings (condos, apartments)
            if 'BUILDING_NAME' in address:
                building_key = f"{address.get('STR_NUM')}-{address.get('STR_NAME')}-{address.get('BUILDING_NAME')}"
                buildings[building_key].append(address)
            # For single-family homes, group by street
            else:
                street_key = f"{address.get('STR_NAME')}-HOMES"
                buildings[street_key].append(address)
        
        # Sort buildings by number of addresses (descending)
        sorted_buildings = sorted(buildings.items(), key=lambda x: len(x[1]), reverse=True)
        
        return sorted_buildings
    return []

# Generate search suggestions based on partial input
def generate_search_suggestions(addresses, partial_query):
    if not partial_query or len(partial_query) < 2:
        return []
    
    suggestions = set()
    partial_query = partial_query.lower()
    
    for address in addresses:
        # Check owner names
        owner1 = str(address.get('OWNER1', '')).lower()
        if partial_query in owner1:
            suggestions.add(address.get('OWNER1', ''))
        
        owner2 = str(address.get('OWNER2', '')).lower()
        if owner2 and partial_query in owner2:
            suggestions.add(address.get('OWNER2', ''))
        
        # Check street address
        street_address = str(address.get('SITE_ADDRESS', '')).lower()
        if partial_query in street_address:
            suggestions.add(address.get('SITE_ADDRESS', ''))
        
        # Check street name
        street_name = str(address.get('STR_NAME', '')).lower()
        if partial_query in street_name:
            suggestions.add(address.get('STR_NAME', ''))
    
    # Convert to list and sort
    suggestion_list = sorted(list(suggestions))
    
    # Limit to top 10 suggestions
    return suggestion_list[:10]

# Filter addresses based on search query and filters
def filter_addresses(addresses, search_query="", show_visited=True, show_not_visited=True, property_type="All", geographic_section="All"):
    filtered = []
    
    for address in addresses:
        # Check if address has been visited
        address_key = address.get('PARCEL_NUMBER', '')
        is_visited = address_key in st.session_state.visited_addresses
        
        # Skip if we're not showing visited addresses and this one has been visited
        if not show_visited and is_visited:
            continue
        
        # Skip if we're not showing unvisited addresses and this one hasn't been visited
        if not show_not_visited and not is_visited:
            continue
        
        # Filter by property type
        if property_type != "All":
            address_property_type = address.get('PROPERTY_USE', '')
            if property_type == "Residential" and address_property_type != "Residential":
                continue
            if property_type == "Business" and address_property_type != "Business":
                continue
        
        # Filter by geographic section
        if geographic_section != "All":
            address_section = address.get('SECTION', '')
            if geographic_section != address_section:
                continue
        
        # Filter by search query
        if search_query:
            query = search_query.lower()
            owner1 = str(address.get('OWNER1', '')).lower()
            owner2 = str(address.get('OWNER2', '')).lower()
            addr = str(address.get('SITE_ADDRESS', '')).lower()
            city_zip = str(address.get('SITE_CITYZIP', '')).lower()
            
            if (query in owner1 or query in owner2 or 
                query in addr or query in city_zip):
                filtered.append(address)
        else:
            filtered.append(address)
    
    return filtered

# Get support level label
def get_support_level_label(level):
    levels = {
        "strong_support": "Strong Support",
        "lean_support": "Lean Support",
        "undecided": "Undecided",
        "lean_against": "Lean Against",
        "strong_against": "Strong Against",
        "unknown": "Unknown"
    }
    return levels.get(level, "Unknown")

# Get support level color
def get_support_level_color(level):
    colors = {
        "strong_support": "darkgreen",
        "lean_support": "lightgreen",
        "undecided": "gray",
        "lean_against": "orange",
        "strong_against": "red",
        "unknown": "lightgray"
    }
    return colors.get(level, "lightgray")

# Get user's current location
def get_user_location():
    st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            const data = {
                lat: lat,
                lon: lon
            };
            window.parent.postMessage({
                type: "streamlit:setComponentValue",
                value: JSON.stringify(data)
            }, "*");
        },
        (error) => {
            console.error("Error getting location:", error);
        }
    );
    </script>
    """, unsafe_allow_html=True)

# Main app layout
if st.session_state.current_page == "home":
    # Organize addresses by precinct if not already done
    organize_addresses_by_precinct()
    
    # Main content area
    st.title("District 6 Canvassing App")
    
    # Display JSON load error if any
    if st.session_state.json_load_error:
        st.error(f"Error loading address data: {st.session_state.json_load_error}")
        st.info("Using fallback data or sample addresses. You can upload a properly formatted JSON file using the uploader in the sidebar.")
    
    # Geographic section selection
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Geographic section selection
        section_options = ["All", "North", "South", "East", "West"]
        st.session_state.geographic_section = st.selectbox(
            "Select Geographic Section:", 
            section_options, 
            index=section_options.index(st.session_state.geographic_section)
        )
    
    with col2:
        # Precinct selection based on geographic section
        precincts = get_district6_precincts()
        
        # Filter precincts by selected geographic section
        if st.session_state.geographic_section != "All":
            filtered_precincts = [p for p in precincts if p['section'] == st.session_state.geographic_section]
        else:
            filtered_precincts = precincts
        
        precinct_options = [f"{p['name']} ({len(st.session_state.precinct_addresses.get(p['id'], []))} addresses)" for p in filtered_precincts]
        
        if precinct_options:
            selected_index = 0
            if st.session_state.selected_precinct:
                for i, p in enumerate(filtered_precincts):
                    if p['id'] == st.session_state.selected_precinct:
                        selected_index = i
                        break
            
            selected_precinct_display = st.selectbox("Select Precinct:", precinct_options, index=min(selected_index, len(precinct_options)-1))
            selected_precinct_index = precinct_options.index(selected_precinct_display)
            st.session_state.selected_precinct = filtered_precincts[selected_precinct_index]['id']
        else:
            st.warning(f"No precincts found in the {st.session_state.geographic_section} section.")
            st.session_state.selected_precinct = None
    
    with col3:
        # Volunteer name input
        st.session_state.volunteer_name = st.text_input("Volunteer Name:", value=st.session_state.volunteer_name)
    
    # Location finder
    st.subheader("Location Finder")
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("📍 Find My Location"):
            # In a real app, this would use the browser's geolocation API
            # For demonstration, we'll use a placeholder
            st.session_state.user_location = {
                "lat": 27.773056,  # St. Petersburg latitude
                "lon": -82.639999  # St. Petersburg longitude
            }
            st.success("Location found! Map updated to show your current position.")
    
    with col2:
        if st.session_state.user_location:
            st.write(f"Your current location: {st.session_state.user_location['lat']:.6f}, {st.session_state.user_location['lon']:.6f}")
            st.write("The map below will show nearby addresses.")
        else:
            st.write("Click 'Find My Location' to see your position on the map and find nearby addresses.")
    
    # Display precinct information
    if st.session_state.selected_precinct:
        precinct_id = st.session_state.selected_precinct
        precinct_info = next((p for p in precincts if p['id'] == precinct_id), None)
        
        if precinct_info:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Registered Voters", precinct_info['total_addresses'])
            
            with col2:
                st.metric("Turnout", precinct_info['turnout'])
            
            with col3:
                # Count visited addresses in this precinct
                precinct_addresses = st.session_state.precinct_addresses.get(precinct_id, [])
                visited_count = sum(1 for addr in precinct_addresses if addr.get('PARCEL_NUMBER', '') in st.session_state.visited_addresses)
                st.metric("Addresses Visited", f"{visited_count}/{len(precinct_addresses)}")
            
            with col4:
                st.metric("Geographic Section", precinct_info['section'])
        
        # Get addresses for the selected precinct
        precinct_addresses = st.session_state.precinct_addresses.get(precinct_id, [])
        
        # Search and filter options
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            # Predictive search with autocomplete
            search_query = st.text_input("Search by name or address:", value=st.session_state.search_query)
            
            # Generate suggestions based on partial input
            if search_query and len(search_query) >= 2 and search_query != st.session_state.search_query:
                st.session_state.search_suggestions = generate_search_suggestions(precinct_addresses, search_query)
            
            # Display suggestions if available
            if st.session_state.search_suggestions and search_query:
                suggestion_container = st.container()
                with suggestion_container:
                    st.markdown("### Suggestions:")
                    for suggestion in st.session_state.search_suggestions:
                        if st.button(f"🔍 {suggestion}", key=f"suggestion_{suggestion}"):
                            search_query = suggestion
                            st.session_state.search_query = suggestion
                            st.rerun()
            
            st.session_state.search_query = search_query
        
        with col2:
            show_visited = st.checkbox("Show Visited", value=True)
        
        with col3:
            show_not_visited = st.checkbox("Show Not Visited", value=True)
        
        with col4:
            property_type = st.selectbox("Property Type:", ["All", "Residential", "Business"])
        
        # Toggle between clustered and individual view
        st.session_state.cluster_view = st.checkbox("Group addresses by building/neighborhood", value=st.session_state.cluster_view)
        
        # Filter addresses based on search and filters
        filtered_addresses = filter_addresses(
            precinct_addresses, 
            search_query=search_query,
            show_visited=show_visited,
            show_not_visited=show_not_visited,
            property_type=property_type,
            geographic_section=st.session_state.geographic_section
        )
        
        # Display map of addresses
        if filtered_addresses:
            st.subheader("Map View")
            
            # Extract coordinates for map
            map_data = []
            for address in filtered_addresses:
                # Use the LAT and LON fields we added during processing
                lat = address.get('LAT')
                lon = address.get('LON')
                
                if lat and lon:
                    map_data.append({
                        "lat": lat, 
                        "lon": lon,
                        "name": address.get('OWNER1', ''),
                        "address": address.get('SITE_ADDRESS', '')
                    })
            
            # Add user's location to the map if available
            if st.session_state.user_location:
                map_data.append({
                    "lat": st.session_state.user_location["lat"],
                    "lon": st.session_state.user_location["lon"],
                    "name": "YOUR LOCATION",
                    "address": "You are here"
                })
            
            # Convert to DataFrame for Streamlit's map
            if map_data:
                map_df = pd.DataFrame(map_data)
                st.map(map_df)
            else:
                st.warning("No map data available for these addresses.")
        
        # Display addresses
        if filtered_addresses:
            st.subheader("Address List")
            
            if st.session_state.cluster_view:
                # Group addresses by building/neighborhood using simple method
                if len(filtered_addresses) > 0:
                    # First try to group by building name if available
                    buildings = defaultdict(list)
                    
                    # Group addresses by building
                    for address in filtered_addresses:
                        # For multi-unit buildings (condos, apartments)
                        if 'BUILDING_NAME' in address:
                            building_key = f"{address.get('STR_NUM')}-{address.get('STR_NAME')}-{address.get('BUILDING_NAME')}"
                            buildings[building_key].append(address)
                        # For single-family homes, group by street
                        else:
                            street_key = f"{address.get('STR_NAME')}-HOMES"
                            buildings[street_key].append(address)
                    
                    # Sort buildings by number of addresses (descending)
                    sorted_buildings = sorted(buildings.items(), key=lambda x: len(x[1]), reverse=True)
                else:
                    sorted_buildings = []
                
                # Display buildings
                for building_key, building_addresses in sorted_buildings:
                    # Extract building name or street name
                    if "-HOMES" in building_key:
                        street_name = building_key.split("-HOMES")[0]
                        building_display = f"{street_name} Street ({len(building_addresses)} homes)"
                        is_building = False
                    else:
                        building_name = building_addresses[0].get('BUILDING_NAME', 'Building')
                        building_display = f"{building_name} ({len(building_addresses)} units)"
                        is_building = True
                    
                    # Create an expander for each building
                    with st.expander(building_display):
                        # Display addresses in this building
                        for i, address in enumerate(building_addresses):
                            address_key = address.get('PARCEL_NUMBER', '')
                            is_visited = address_key in st.session_state.visited_addresses
                            
                            # Get support level if available
                            support_level = st.session_state.support_levels.get(address_key, "unknown")
                            support_label = get_support_level_label(support_level)
                            support_color = get_support_level_color(support_level)
                            
                            # Check if this is Ariel's address
                            is_ariel = False
                            owner1 = str(address.get('OWNER1', ''))
                            if "FERNANDEZ, ARIEL" in owner1:
                                is_ariel = True
                            
                            # Create a card-like display for each address
                            col1, col2, col3 = st.columns([3, 1, 1])
                            
                            with col1:
                                # Format address display
                                site_address = address.get('SITE_ADDRESS', '')
                                site_cityzip = address.get('SITE_CITYZIP', '')
                                owner1 = address.get('OWNER1', '')
                                owner2 = address.get('OWNER2', '')
                                section = address.get('SECTION', '')
                                
                                # Highlight Ariel's address
                                if is_ariel:
                                    st.markdown(f"⭐ **{owner1}** ⭐")
                                    st.markdown(f"**{site_address}**  \n{site_cityzip}")
                                    st.markdown(f"Section: {section}")
                                else:
                                    st.markdown(f"**{owner1}**{' & ' + owner2 if owner2 else ''}")
                                    st.markdown(f"{site_address}  \n{site_cityzip}")
                                    st.markdown(f"Section: {section}")
                                
                                # Show property type
                                property_use = address.get('PROPERTY_USE', '')
                                st.markdown(f"*{property_use}*")
                                
                                # Show support level if available
                                if support_level != "unknown":
                                    st.markdown(f"Support Level: <span style='color:{support_color};font-weight:bold'>{support_label}</span>", unsafe_allow_html=True)
                                
                                # Show donation amount if available
                                donation = st.session_state.donations.get(address_key, 0)
                                if donation > 0:
                                    st.markdown(f"Donation: **${donation:.2f}**")
                            
                            with col2:
                                # Contact button
                                if st.button(f"Contact {i}", key=f"contact_{address_key}"):
                                    navigate_to("contact", address)
                            
                            with col3:
                                # Mark as visited/not visited
                                if is_visited:
                                    if st.button(f"✓ Visited {i}", key=f"visited_{address_key}"):
                                        st.session_state.visited_addresses.remove(address_key)
                                        st.rerun()
                                else:
                                    col3a, col3b = st.columns(2)
                                    with col3a:
                                        if st.button(f"Not Home {i}", key=f"nothome_{address_key}"):
                                            st.session_state.visited_addresses.add(address_key)
                                            st.session_state.interaction_notes[address_key] = "Not home"
                                            st.rerun()
                                    with col3b:
                                        if st.button(f"Skip {i}", key=f"skip_{address_key}"):
                                            st.session_state.visited_addresses.add(address_key)
                                            st.session_state.interaction_notes[address_key] = "Skipped"
                                            st.rerun()
                            
                            st.markdown("---")
            else:
                # Display individual addresses
                for i, address in enumerate(filtered_addresses):
                    address_key = address.get('PARCEL_NUMBER', '')
                    is_visited = address_key in st.session_state.visited_addresses
                    
                    # Get support level if available
                    support_level = st.session_state.support_levels.get(address_key, "unknown")
                    support_label = get_support_level_label(support_level)
                    support_color = get_support_level_color(support_level)
                    
                    # Check if this is Ariel's address
                    is_ariel = False
                    owner1 = str(address.get('OWNER1', ''))
                    if "FERNANDEZ, ARIEL" in owner1:
                        is_ariel = True
                    
                    # Create a card-like display for each address
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        # Format address display
                        site_address = address.get('SITE_ADDRESS', '')
                        site_cityzip = address.get('SITE_CITYZIP', '')
                        owner1 = address.get('OWNER1', '')
                        owner2 = address.get('OWNER2', '')
                        section = address.get('SECTION', '')
                        
                        # Highlight Ariel's address
                        if is_ariel:
                            st.markdown(f"⭐ **{owner1}** ⭐")
                            st.markdown(f"**{site_address}**  \n{site_cityzip}")
                            st.markdown(f"Section: {section}")
                        else:
                            st.markdown(f"**{owner1}**{' & ' + owner2 if owner2 else ''}")
                            st.markdown(f"{site_address}  \n{site_cityzip}")
                            st.markdown(f"Section: {section}")
                        
                        # Show property type
                        property_use = address.get('PROPERTY_USE', '')
                        st.markdown(f"*{property_use}*")
                        
                        # Show support level if available
                        if support_level != "unknown":
                            st.markdown(f"Support Level: <span style='color:{support_color};font-weight:bold'>{support_label}</span>", unsafe_allow_html=True)
                        
                        # Show donation amount if available
                        donation = st.session_state.donations.get(address_key, 0)
                        if donation > 0:
                            st.markdown(f"Donation: **${donation:.2f}**")
                    
                    with col2:
                        # Contact button
                        if st.button(f"Contact {i}", key=f"contact_{address_key}"):
                            navigate_to("contact", address)
                    
                    with col3:
                        # Mark as visited/not visited
                        if is_visited:
                            if st.button(f"✓ Visited {i}", key=f"visited_{address_key}"):
                                st.session_state.visited_addresses.remove(address_key)
                                st.rerun()
                        else:
                            col3a, col3b = st.columns(2)
                            with col3a:
                                if st.button(f"Not Home {i}", key=f"nothome_{address_key}"):
                                    st.session_state.visited_addresses.add(address_key)
                                    st.session_state.interaction_notes[address_key] = "Not home"
                                    st.rerun()
                            with col3b:
                                if st.button(f"Skip {i}", key=f"skip_{address_key}"):
                                    st.session_state.visited_addresses.add(address_key)
                                    st.session_state.interaction_notes[address_key] = "Skipped"
                                    st.rerun()
                    
                    st.markdown("---")
        else:
            st.warning("No addresses found matching your criteria.")

elif st.session_state.current_page == "contact":
    # Contact page for recording interactions
    st.title("Contact Information")
    
    if st.session_state.contact_address:
        address = st.session_state.contact_address
        address_key = address.get('PARCEL_NUMBER', '')
        
        # Display address information
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Format address display
            site_address = address.get('SITE_ADDRESS', '')
            site_cityzip = address.get('SITE_CITYZIP', '')
            owner1 = address.get('OWNER1', '')
            owner2 = address.get('OWNER2', '')
            section = address.get('SECTION', '')
            
            st.markdown(f"## {owner1}{' & ' + owner2 if owner2 else ''}")
            st.markdown(f"### {site_address}  \n{site_cityzip}")
            st.markdown(f"Section: {section}")
            
            # Show property type
            property_use = address.get('PROPERTY_USE', '')
            st.markdown(f"*{property_use}*")
        
        with col2:
            # Back button
            if st.button("Back to List"):
                navigate_to("home")
        
        # Support level selection
        st.subheader("Support Level")
        current_support = st.session_state.support_levels.get(address_key, "unknown")
        support_options = {
            "strong_support": "Strong Support",
            "lean_support": "Lean Support",
            "undecided": "Undecided",
            "lean_against": "Lean Against",
            "strong_against": "Strong Against",
            "unknown": "Unknown"
        }
        
        support_level = st.radio(
            "Select support level:",
            list(support_options.keys()),
            format_func=lambda x: support_options[x],
            index=list(support_options.keys()).index(current_support)
        )
        
        # Donation tracking
        st.subheader("Donation")
        current_donation = st.session_state.donations.get(address_key, 0)
        donation_amount = st.number_input("Donation amount ($):", min_value=0.0, value=float(current_donation), step=5.0)
        
        # Interaction notes
        st.subheader("Interaction Notes")
        current_notes = st.session_state.interaction_notes.get(address_key, "")
        
        # Quick tags
        st.markdown("Quick Tags:")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👍 Supportive"):
                current_notes += " [Supportive]"
        
        with col2:
            if st.button("❓ Needs Info"):
                current_notes += " [Needs Info]"
        
        with col3:
            if st.button("📞 Call Back"):
                current_notes += " [Call Back]"
        
        with col4:
            if st.button("🚫 Do Not Contact"):
                current_notes += " [Do Not Contact]"
        
        # Free-form notes
        notes = st.text_area("Notes:", value=current_notes, height=150)
        
        # Follow-up checkbox
        follow_up = st.checkbox("Flag for follow-up")
        
        # Save button
        if st.button("Save Contact Information"):
            # Save all the information
            st.session_state.support_levels[address_key] = support_level
            st.session_state.donations[address_key] = donation_amount
            st.session_state.interaction_notes[address_key] = notes
            
            # Mark as visited
            st.session_state.visited_addresses.add(address_key)
            
            # Add follow-up tag if checked
            if follow_up and "[Follow Up]" not in notes:
                st.session_state.interaction_notes[address_key] += " [Follow Up]"
            
            st.success("Contact information saved!")
            
            # Return to the home page
            navigate_to("home")
    else:
        st.error("No address selected for contact.")
        if st.button("Return to Home"):
            navigate_to("home")

# Add debug information in sidebar
with st.sidebar.expander("Debug Information"):
    st.write("Current Directory:")
    st.code(os.getcwd())
    
    st.write("Available Files:")
    file_list = os.listdir()
    st.write(file_list)
    
    if os.path.exists('/home/ubuntu/upload'):
        st.write("Upload Directory Files:")
        upload_files = os.listdir('/home/ubuntu/upload')
        st.write(upload_files)
    
    st.write("Fixed JSON File Status:")
    if os.path.exists('/home/ubuntu/fixed_addresses.json'):
        st.success("Fixed addresses.json file exists")
    else:
        st.error("Fixed addresses.json file not found")
    
    st.write("User Location:")
    st.write(st.session_state.user_location)
    
    # Show sample data checkbox
    use_sample_data = st.checkbox("Use Sample Data", value=True)
    if use_sample_data and not st.session_state.data_loaded:
        st.session_state.address_data = generate_sample_addresses()
        st.session_state.data_loaded = True
        st.success("Using sample data with all addresses")
        st.rerun()

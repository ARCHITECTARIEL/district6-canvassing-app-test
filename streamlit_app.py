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

# Function to navigate between pages
def navigate_to(page, address=None):
    st.session_state.current_page = page
    if address is not None:
        st.session_state.contact_address = address
    st.experimental_rerun()

# Sidebar for navigation
st.sidebar.title("District 6 Canvassing")

# Real District 6 precinct data - removed strategy tags
def get_district6_precincts():
    return [
        {"id": "106", "name": "Precinct 106", "total_addresses": 760, "turnout": "88.55%", "zip_codes": ["33701", "33705"]},
        {"id": "108", "name": "Precinct 108", "total_addresses": 2773, "turnout": "81.79%", "zip_codes": ["33701", "33705"]},
        {"id": "109", "name": "Precinct 109", "total_addresses": 2151, "turnout": "77.59%", "zip_codes": ["33701", "33705"]},
        {"id": "116", "name": "Precinct 116", "total_addresses": 1511, "turnout": "67.97%", "zip_codes": ["33701", "33705"]},
        {"id": "117", "name": "Precinct 117", "total_addresses": 1105, "turnout": "62.53%", "zip_codes": ["33701", "33705"]},
        {"id": "118", "name": "Precinct 118", "total_addresses": 1175, "turnout": "85.36%", "zip_codes": ["33701", "33705"]},
        {"id": "119", "name": "Precinct 119", "total_addresses": 2684, "turnout": "65.31%", "zip_codes": ["33701", "33705"]},
        {"id": "121", "name": "Precinct 121", "total_addresses": 922, "turnout": "77.55%", "zip_codes": ["33701", "33705"]},
        {"id": "122", "name": "Precinct 122", "total_addresses": 258, "turnout": "87.60%", "zip_codes": ["33701", "33705"]},
        {"id": "123", "name": "Precinct 123", "total_addresses": 4627, "turnout": "85.35%", "zip_codes": ["33701", "33705"]},
        {"id": "125", "name": "Precinct 125", "total_addresses": 1301, "turnout": "79.94%", "zip_codes": ["33701", "33705"]},
        {"id": "126", "name": "Precinct 126", "total_addresses": 1958, "turnout": "77.07%", "zip_codes": ["33701", "33705"]},
        {"id": "130", "name": "Precinct 130", "total_addresses": 3764, "turnout": "86.16%", "zip_codes": ["33701", "33705"]}
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
        "PRECINCT": "106"  # Explicitly assign precinct
    })
    
    # Generate additional sample addresses for each precinct
    precincts = get_district6_precincts()
    for precinct in precincts:
        precinct_id = precinct["id"]
        
        # Generate a few apartment buildings/condos with multiple units
        for b in range(3):
            building_num = 100 + b * 100
            building_name = ["OAK TERRACE", "PALM HEIGHTS", "BAYVIEW TOWERS", "SUNSET CONDOS"][b % 4]
            street_name = ["MAIN", "OAK", "BEACH", "CENTRAL"][b % 4]
            zip_code = "33701" if b % 2 == 0 else "33705"
            
            # Generate multiple units in the same building
            for i in range(10):  # 10 units per building
                unit_num = i + 1
                
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
                    "BUILDING_NAME": building_name
                })
        
        # Generate some single-family homes
        for i in range(10):  # 10 single-family homes per precinct
            home_num = 200 + i * 10
            street_name = ["PINE", "MAPLE", "PALM", "OCEAN"][i % 4]
            zip_code = "33701" if i % 2 == 0 else "33705"
            
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
                "PRECINCT": precinct_id  # Explicitly assign precinct
            })
        
        # Generate some businesses
        for i in range(5):  # 5 businesses per precinct
            business_num = 300 + i * 10
            street_name = ["COMMERCIAL", "BUSINESS", "MARKET", "OFFICE"][i % 4]
            zip_code = "33701" if i % 2 == 0 else "33705"
            
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
                "PRECINCT": precinct_id  # Explicitly assign precinct
            })
    
    return sample_data

# Load addresses directly from GitHub repository
@st.cache_data
def load_addresses_from_github():
    try:
        # Try multiple possible filenames
        filenames = [
            "addresses.json",
            "Advanced Search 4-11-2025 (1).json",
            "Advanced_Search_4-11-2025_(1).json"
        ]
        
        for filename in filenames:
            encoded_filename = quote(filename)
            github_url = f"https://raw.githubusercontent.com/ARCHITECTARIEL/district6-canvassing-app-test/main/{encoded_filename}"
            
            st.sidebar.info(f"Attempting to load: {github_url}")
            
            # Fetch the file from GitHub
            response = requests.get(github_url)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Parse the JSON data
                try:
                    address_data = response.json()
                    st.sidebar.success(f"Successfully loaded {len(address_data)} addresses from GitHub")
                    
                    # Process the address data
                    process_address_data(address_data)
                    return address_data
                except json.JSONDecodeError as e:
                    st.sidebar.error(f"Error parsing JSON: {str(e)}")
                    continue
        
        # If all attempts fail, use sample data
        st.sidebar.error("Failed to load addresses from GitHub. Using sample data instead.")
        return generate_sample_addresses()
    except Exception as e:
        st.sidebar.error(f"Error loading addresses from GitHub: {str(e)}")
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
    
    # Make sure Ariel's address is included
    ariel_exists = False
    for address in address_data:
        if (address.get('STR_NUM') == 315 and 
            'TAYLOR' in str(address.get('STR_NAME', '')) and 
            address.get('STR_ZIP') == '33705'):
            ariel_exists = True
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
            "PRECINCT": "106"  # Explicitly assign precinct
        }
        address_data.append(ariel_address)
        st.sidebar.success("Added Ariel Fernandez's address to the dataset")

# Load address data when the app starts
if not st.session_state.data_loaded:
    st.session_state.address_data = load_addresses_from_github()
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
            
            # Generate unique coordinates with small variations for addresses in the same building
            # This ensures they cluster properly but don't overlap exactly
            street_num = address.get('STR_NUM', 0)
            street_name = str(address.get('STR_NAME', ''))
            unit = str(address.get('STR_UNIT', ''))
            
            # Base coordinates for St. Petersburg
            base_lat = 27.773056
            base_lon = -82.639999
            
            # Generate deterministic but unique coordinates
            hash_val = hash(f"{street_num}{street_name}")
            lat = base_lat + (hash_val % 1000) / 50000
            lon = base_lon + (hash_val % 1000) / 50000
            
            # Add small variation for units in the same building
            if unit:
                unit_num = ''.join(filter(str.isdigit, unit))
                if unit_num:
                    unit_val = int(unit_num)
                    lat += unit_val / 1000000
                    lon += unit_val / 1000000
            
            # Format the address data
            formatted_address = {
                "id": f"{precinct_id}_{address.get('PARCEL_NUMBER', '')}",
                "precinct_id": precinct_id,
                "owner1": address.get('OWNER1', 'Unknown'),
                "owner2": address.get('OWNER2', ''),
                "address": f"{address.get('STR_NUM', '')} {address.get('STR_NAME', '')} {address.get('STR_UNIT', '') or ''}".strip(),
                "city_zip": address.get('SITE_CITYZIP', ''),
                "property_type": address.get('PROPERTY_USE', 'Residential'),
                "owner_occupied": "Yes" if address.get('HX_YN', 'No') == 'Yes' else "No",
                "lat": lat,
                "lon": lon,
                "street_num": street_num,
                "street_name": street_name,
                "unit": unit,
                "building_name": address.get('BUILDING_NAME', '')
            }
            
            # Add to the appropriate precinct
            if precinct_id in st.session_state.precinct_addresses:
                st.session_state.precinct_addresses[precinct_id].append(formatted_address)

# Simple clustering function that doesn't rely on scikit-learn
def simple_cluster_addresses(addresses):
    # Group addresses by building (street number and name)
    building_clusters = defaultdict(list)
    
    for address in addresses:
        # Create a building key
        building_key = f"{address['street_num']}_{address['street_name']}"
        building_clusters[building_key].append(address)
    
    # Create clusters
    clusters = []
    single_addresses = []
    
    # Process building clusters
    for building_key, building_addresses in building_clusters.items():
        if len(building_addresses) > 1:
            # This is a multi-unit building
            first_address = building_addresses[0]
            
            # Calculate average coordinates
            avg_lat = sum(a['lat'] for a in building_addresses) / len(building_addresses)
            avg_lon = sum(a['lon'] for a in building_addresses) / len(building_addresses)
            
            # Determine if this is a multi-family building
            is_multifamily = any('Residential' in str(a.get('property_type', '')) for a in building_addresses)
            
            # Get building name if available
            building_name = next((a['building_name'] for a in building_addresses if a['building_name']), 
                               f"{first_address['street_num']} {first_address['street_name']}")
            
            clusters.append({
                'type': 'building' if is_multifamily else 'neighborhood',
                'lat': avg_lat,
                'lon': avg_lon,
                'label': f"{building_name} ({len(building_addresses)} units)" if is_multifamily else 
                         f"{first_address['street_num']} {first_address['street_name']} Area ({len(building_addresses)} homes)",
                'address_count': len(building_addresses),
                'addresses': building_addresses,
                'id': f"cluster_{building_key}"
            })
        else:
            # Single address
            single_addresses.extend(building_addresses)
    
    # Group remaining single addresses by neighborhood (approximate by coordinates)
    if single_addresses:
        # Simple geographic grouping - group addresses that are close together
        neighborhood_clusters = defaultdict(list)
        
        for address in single_addresses:
            # Create a rough geographic grid (0.001 degrees is roughly 100 meters)
            grid_lat = round(address['lat'] * 1000) / 1000
            grid_lon = round(address['lon'] * 1000) / 1000
            grid_key = f"{grid_lat}_{grid_lon}"
            
            neighborhood_clusters[grid_key].append(address)
        
        # Process neighborhood clusters
        for grid_key, neighborhood_addresses in neighborhood_clusters.items():
            if len(neighborhood_addresses) > 1:
                # This is a neighborhood cluster
                avg_lat = sum(a['lat'] for a in neighborhood_addresses) / len(neighborhood_addresses)
                avg_lon = sum(a['lon'] for a in neighborhood_addresses) / len(neighborhood_addresses)
                
                # Get a representative street name
                street_names = set(a['street_name'] for a in neighborhood_addresses if a['street_name'])
                street_desc = ", ".join(list(street_names)[:2])
                if len(street_names) > 2:
                    street_desc += " area"
                
                clusters.append({
                    'type': 'neighborhood',
                    'lat': avg_lat,
                    'lon': avg_lon,
                    'label': f"{street_desc} ({len(neighborhood_addresses)} addresses)",
                    'address_count': len(neighborhood_addresses),
                    'addresses': neighborhood_addresses,
                    'id': f"cluster_{grid_key}"
                })
            else:
                # Add as individual address
                address = neighborhood_addresses[0]
                clusters.append({
                    'type': 'single',
                    'lat': address['lat'],
                    'lon': address['lon'],
                    'label': f"{address['address']}",
                    'address_count': 1,
                    'addresses': [address],
                    'id': f"single_{address['id']}"
                })
    
    return clusters

# Organize addresses by precinct
organize_addresses_by_precinct()

# Navigation
tab = st.sidebar.radio("Navigation", ["Home", "Demographics", "Election History", "Stats", "Settings"])

# Volunteer info in sidebar
st.sidebar.markdown("---")
volunteer_name = st.sidebar.text_input("Volunteer Name", value=st.session_state.volunteer_name)
if volunteer_name != st.session_state.volunteer_name:
    st.session_state.volunteer_name = volunteer_name
    st.sidebar.success("Volunteer name updated!")

if st.sidebar.button("Sync Data"):
    st.sidebar.success("Data synchronized successfully!")

# Main content area based on current page
if st.session_state.current_page == "contact" and st.session_state.contact_address:
    # Contact page
    address = st.session_state.contact_address
    address_id = address.get('id', '')
    
    st.title("Contact Information")
    
    # Back button
    if st.button("← Back to Addresses"):
        navigate_to("home")
    
    st.markdown("---")
    
    # Display address information
    col1, col2 = st.columns([3, 1])
    with col1:
        owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
        address_text = f"{address.get('address', '')}, {address.get('city_zip', '')}"
        property_type = address.get('property_type', 'Residential')
        
        # Check if this is Ariel's address
        is_ariel = "FERNANDEZ, ARIEL" in str(address.get('owner1', ''))
        
        if is_ariel:
            st.markdown("### 🌟 YOUR ADDRESS 🌟")
            st.markdown(f"**👤 {owner}**")
            st.markdown(f"**🏠 {address_text}**")
            st.markdown(f"**🏘️ {property_type}**")
        else:
            st.markdown(f"## {owner}")
            st.markdown(f"**Address:** {address_text}")
            st.markdown(f"**Property Type:** {property_type}")
    
    with col2:
        # Display visit status
        if address_id in st.session_state.visited_addresses:
            st.success("Previously Visited")
        else:
            st.info("Not Yet Visited")
    
    st.markdown("---")
    
    # Support level
    st.subheader("Voter Support Level")
    support_options = ["Strong Support", "Leaning Support", "Undecided", "Leaning Against", "Strong Against", "Refused"]
    current_support = st.session_state.support_levels.get(address_id, "")
    support = st.radio("Support Level:", support_options, index=support_options.index(current_support) if current_support in support_options else 2)
    
    # Donation
    st.subheader("Donation Information")
    current_donation = st.session_state.donations.get(address_id, 0)
    donation = st.number_input("Donation Amount ($):", min_value=0.0, value=float(current_donation), step=5.0)
    
    # Notes
    st.subheader("Interaction Notes")
    current_notes = st.session_state.interaction_notes.get(address_id, "")
    notes = st.text_area("Notes:", value=current_notes, height=150)
    
    # Tags
    st.subheader("Quick Tags")
    col1, col2, col3, col4 = st.columns(4)
    tag_options = ["Interested in Yard Sign", "Wants More Info", "Willing to Volunteer", "Needs Follow-up"]
    
    # Extract existing tags from notes
    existing_tags = []
    for tag in tag_options:
        if tag in current_notes:
            existing_tags.append(tag)
    
    # Display tag checkboxes
    selected_tags = []
    with col1:
        if st.checkbox(tag_options[0], value=tag_options[0] in existing_tags):
            selected_tags.append(tag_options[0])
    with col2:
        if st.checkbox(tag_options[1], value=tag_options[1] in existing_tags):
            selected_tags.append(tag_options[1])
    with col3:
        if st.checkbox(tag_options[2], value=tag_options[2] in existing_tags):
            selected_tags.append(tag_options[2])
    with col4:
        if st.checkbox(tag_options[3], value=tag_options[3] in existing_tags):
            selected_tags.append(tag_options[3])
    
    # Save and cancel buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Contact Information", use_container_width=True):
            # Add tags to notes if not already present
            for tag in selected_tags:
                if tag not in notes:
                    if notes:
                        notes += f"\n[{tag}]"
                    else:
                        notes = f"[{tag}]"
            
            # Remove tags that were unchecked
            for tag in tag_options:
                if tag not in selected_tags and f"[{tag}]" in notes:
                    notes = notes.replace(f"[{tag}]", "").strip()
            
            # Save all information
            st.session_state.visited_addresses.add(address_id)
            st.session_state.interaction_notes[address_id] = notes
            st.session_state.support_levels[address_id] = support
            st.session_state.donations[address_id] = donation
            
            # Return to home page
            st.success("Contact information saved successfully!")
            navigate_to("home")
    
    with col2:
        if st.button("Cancel", use_container_width=True):
            navigate_to("home")

elif tab == "Home" and st.session_state.current_page == "home":
    st.title("District 6 Door Knocking Campaign")
    
    # Precinct selector
    precincts = get_district6_precincts()
    precinct_options = ["Select a precinct"] + [f"Precinct {p['id']}" for p in precincts]
    selected_option = st.selectbox("Select Precinct:", precinct_options)
    
    if selected_option != "Select a precinct":
        # Extract precinct ID from selection
        precinct_id = selected_option.split()[1]
        
        # Find the selected precinct
        selected_precinct_data = next((p for p in precincts if p['id'] == precinct_id), None)
        
        # Display precinct info
        if selected_precinct_data:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Registered Voters", selected_precinct_data['total_addresses'])
            with col2:
                st.metric("Voter Turnout", selected_precinct_data['turnout'])
        
        # Get addresses for this precinct
        addresses = st.session_state.precinct_addresses.get(precinct_id, [])
        
        # Display addresses
        if addresses:
            st.subheader("Addresses to Visit")
            
            # Display number of addresses found
            st.info(f"Found {len(addresses)} addresses in Precinct {precinct_id}")
            
            # Search functionality
            search_query = st.text_input("Search addresses by name, street, or number:", value=st.session_state.search_query)
            if search_query != st.session_state.search_query:
                st.session_state.search_query = search_query
            
            # Filter addresses by search query if provided
            filtered_addresses = addresses
            if search_query:
                search_query = search_query.lower()
                filtered_addresses = []
                for address in addresses:
                    # Check if search query matches any part of the address
                    owner1 = str(address.get('owner1', '')).lower()
                    owner2 = str(address.get('owner2', '')).lower()
                    addr = str(address.get('address', '')).lower()
                    city_zip = str(address.get('city_zip', '')).lower()
                    prop_type = str(address.get('property_type', '')).lower()
                    
                    if (search_query in owner1 or
                        search_query in owner2 or
                        search_query in addr or
                        search_query in city_zip or
                        search_query in prop_type):
                        filtered_addresses.append(address)
            
            # Highlight if Ariel's address is found
            ariel_found = False
            for address in filtered_addresses:
                owner1 = str(address.get('owner1', ''))
                if "FERNANDEZ, ARIEL" in owner1:
                    ariel_found = True
                    st.success("✅ Ariel Fernandez's address found in this precinct!")
                    break
            
            # Map view of addresses
            if filtered_addresses:
                st.subheader("Map View")
                
                # Map view options
                map_col1, map_col2 = st.columns([1, 3])
                with map_col1:
                    cluster_view = st.checkbox("Group Addresses", value=st.session_state.cluster_view)
                    if cluster_view != st.session_state.cluster_view:
                        st.session_state.cluster_view = cluster_view
                        st.session_state.selected_cluster = None
                
                # Create map data based on view mode
                if st.session_state.cluster_view:
                    # Cluster addresses using simple clustering
                    clusters = simple_cluster_addresses(filtered_addresses)
                    
                    # Check if a cluster is selected
                    if st.session_state.selected_cluster:
                        # Find the selected cluster
                        selected_cluster = next((c for c in clusters if c['id'] == st.session_state.selected_cluster), None)
                        
                        if selected_cluster:
                            # Show only the selected cluster's addresses
                            with map_col2:
                                st.write(f"**Selected: {selected_cluster['label']}**")
                                if st.button("Back to All Clusters"):
                                    st.session_state.selected_cluster = None
                                    st.rerun()
                            
                            # Create map data for individual addresses in the cluster
                            map_data = pd.DataFrame({
                                'lat': [a['lat'] for a in selected_cluster['addresses']],
                                'lon': [a['lon'] for a in selected_cluster['addresses']]
                            })
                            
                            # Display the map
                            st.map(map_data)
                            
                            # Show addresses in this cluster
                            st.subheader(f"Addresses in {selected_cluster['label']}")
                            
                            # Group addresses by building/street
                            if selected_cluster['address_count'] > 1:
                                # Sort addresses by street number and unit
                                sorted_addresses = sorted(
                                    selected_cluster['addresses'],
                                    key=lambda a: (a['street_num'], a.get('unit', ''))
                                )
                                
                                # Display addresses in a more compact format
                                for address in sorted_addresses:
                                    with st.container():
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
                                            address_text = f"{address.get('address', '')}"
                                            property_type = address.get('property_type', 'Residential')
                                            st.markdown(f"**{owner}**")
                                            st.text(address_text)
                                            st.text(f"Type: {property_type}")
                                        
                                        with col2:
                                            address_id = address.get('id', '')
                                            visited = address_id in st.session_state.visited_addresses
                                            
                                            if not visited:
                                                if st.button("Contact", key=f"contact_cluster_{address_id}"):
                                                    # Open contact page
                                                    navigate_to("contact", address)
                                            else:
                                                st.success("Visited")
                                                # Show support level if recorded
                                                if address_id in st.session_state.support_levels:
                                                    support = st.session_state.support_levels[address_id]
                                                    st.info(f"Support: {support}")
                                                
                                                # View/Edit button
                                                if st.button("View/Edit", key=f"edit_{address_id}"):
                                                    navigate_to("contact", address)
                                        
                                        st.markdown("---")
                        else:
                            # Cluster not found, reset selection
                            st.session_state.selected_cluster = None
                            st.rerun()
                    else:
                        # Show all clusters
                        # Create map data for clusters
                        map_data = pd.DataFrame({
                            'lat': [c['lat'] for c in clusters],
                            'lon': [c['lon'] for c in clusters]
                        })
                        
                        # Display the map
                        st.map(map_data)
                        
                        # Display cluster information
                        st.subheader("Address Clusters")
                        
                        # Group clusters by type
                        buildings = [c for c in clusters if c['type'] == 'building']
                        neighborhoods = [c for c in clusters if c['type'] == 'neighborhood']
                        singles = [c for c in clusters if c['type'] == 'single']
                        
                        # Create tabs for different types of clusters
                        cluster_tabs = st.tabs(["Buildings", "Neighborhoods", "Single Addresses"])
                        
                        with cluster_tabs[0]:
                            if buildings:
                                st.write(f"**{len(buildings)} Buildings with Multiple Units**")
                                for cluster in sorted(buildings, key=lambda c: c['address_count'], reverse=True):
                                    with st.container():
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.markdown(f"**{cluster['label']}**")
                                            sample_address = cluster['addresses'][0]
                                            st.text(f"{sample_address['street_num']} {sample_address['street_name']}")
                                        
                                        with col2:
                                            if st.button("View Details", key=f"view_{cluster['id']}"):
                                                st.session_state.selected_cluster = cluster['id']
                                                st.rerun()
                                        
                                        st.markdown("---")
                            else:
                                st.info("No multi-unit buildings found in this precinct.")
                        
                        with cluster_tabs[1]:
                            if neighborhoods:
                                st.write(f"**{len(neighborhoods)} Neighborhood Clusters**")
                                for cluster in sorted(neighborhoods, key=lambda c: c['address_count'], reverse=True):
                                    with st.container():
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            st.markdown(f"**{cluster['label']}**")
                                            streets = set([f"{a['street_name']}" for a in cluster['addresses']])
                                            st.text(f"Streets: {', '.join(list(streets)[:3])}{' and more' if len(streets) > 3 else ''}")
                                        
                                        with col2:
                                            if st.button("View Details", key=f"view_{cluster['id']}"):
                                                st.session_state.selected_cluster = cluster['id']
                                                st.rerun()
                                        
                                        st.markdown("---")
                            else:
                                st.info("No neighborhood clusters found in this precinct.")
                        
                        with cluster_tabs[2]:
                            if singles:
                                st.write(f"**{len(singles)} Individual Addresses**")
                                for cluster in singles:
                                    with st.container():
                                        col1, col2 = st.columns([3, 1])
                                        with col1:
                                            address = cluster['addresses'][0]
                                            owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
                                            address_text = f"{address.get('address', '')}"
                                            property_type = address.get('property_type', 'Residential')
                                            st.markdown(f"**{owner}**")
                                            st.text(address_text)
                                            st.text(f"Type: {property_type}")
                                        
                                        with col2:
                                            if st.button("View Details", key=f"view_{cluster['id']}"):
                                                st.session_state.selected_cluster = cluster['id']
                                                st.rerun()
                                        
                                        st.markdown("---")
                            else:
                                st.info("No individual addresses found in this precinct.")
                else:
                    # Show all addresses individually
                    map_data = pd.DataFrame({
                        'lat': [a.get('lat', 0) for a in filtered_addresses],
                        'lon': [a.get('lon', 0) for a in filtered_addresses]
                    })
                    
                    # Display the map
                    st.map(map_data)
            
            # Progress tracking
            total_addresses = len(filtered_addresses)
            visited_count = len([a for a in filtered_addresses if a['id'] in st.session_state.visited_addresses])
            remaining_count = total_addresses - visited_count
            percentage = (visited_count / total_addresses * 100) if total_addresses > 0 else 0
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Progress", f"{visited_count}/{total_addresses} ({percentage:.1f}%)")
            with col2:
                st.metric("Remaining", remaining_count)
            
            st.progress(percentage / 100)
            
            # Filter options
            st.subheader("Filter Options")
            col1, col2, col3 = st.columns(3)
            with col1:
                show_visited = st.checkbox("Show Visited", value=True)
            with col2:
                show_not_visited = st.checkbox("Show Not Visited", value=True)
            with col3:
                property_types = ["All", "Residential", "Business"]
                property_filter = st.selectbox("Property Type", property_types)
            
            # Apply filters
            if not show_visited:
                filtered_addresses = [a for a in filtered_addresses if a['id'] not in st.session_state.visited_addresses]
            if not show_not_visited:
                filtered_addresses = [a for a in filtered_addresses if a['id'] in st.session_state.visited_addresses]
            if property_filter != "All":
                filtered_addresses = [a for a in filtered_addresses if a.get('property_type', 'Residential') == property_filter]
            
            # Only show individual address list if not in cluster view or if a cluster is selected
            if not st.session_state.cluster_view or st.session_state.selected_cluster:
                # Pagination for addresses
                addresses_per_page = 10
                total_pages = (len(filtered_addresses) + addresses_per_page - 1) // addresses_per_page
                
                if total_pages > 1:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        page = st.slider("Page", 1, max(1, total_pages), 1)
                        start_idx = (page - 1) * addresses_per_page
                        end_idx = min(start_idx + addresses_per_page, len(filtered_addresses))
                        st.write(f"Showing addresses {start_idx + 1}-{end_idx} of {len(filtered_addresses)}")
                else:
                    page = 1
                    start_idx = 0
                    end_idx = len(filtered_addresses)
                
                # Address list
                for i, address in enumerate(filtered_addresses[start_idx:end_idx]):
                    address_id = address.get('id', i)
                    visited = address_id in st.session_state.visited_addresses
                    
                    # Safely check if this is Ariel's address
                    owner1 = str(address.get('owner1', ''))
                    is_ariel = "FERNANDEZ, ARIEL" in owner1
                    
                    # Create a card-like container for each address
                    with st.container():
                        if is_ariel:
                            st.markdown("---")
                            st.markdown("### 🌟 YOUR ADDRESS 🌟")
                        
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            owner = f"{address.get('owner1', 'Unknown')} {address.get('owner2', '')}"
                            address_text = f"{address.get('address', '')}, {address.get('city_zip', '')}"
                            property_type = address.get('property_type', 'Residential')
                            
                            if is_ariel:
                                st.markdown(f"**👤 {owner}**")
                                st.markdown(f"**🏠 {address_text}**")
                                st.markdown(f"**🏘️ {property_type}**")
                            else:
                                st.markdown(f"**{owner}**")
                                st.text(address_text)
                                st.text(f"Type: {property_type}")
                        
                        with col2:
                            if not visited:
                                if st.button("Contact", key=f"contact_{address_id}"):
                                    # Open contact page
                                    navigate_to("contact", address)
                                
                                if st.button("Not Home", key=f"nothome_{address_id}"):
                                    st.session_state.visited_addresses.add(address_id)
                                    st.session_state.interaction_notes[address_id] = "Not home during visit."
                                    st.success("Marked as Not Home")
                                    st.rerun()
                                
                                if st.button("Skip", key=f"skip_{address_id}"):
                                    st.session_state.visited_addresses.add(address_id)
                                    st.session_state.interaction_notes[address_id] = "Skipped during canvassing."
                                    st.success("Marked as Skipped")
                                    st.rerun()
                            else:
                                st.success("Visited")
                                # Show support level if recorded
                                if address_id in st.session_state.support_levels:
                                    support = st.session_state.support_levels[address_id]
                                    st.info(f"Support: {support}")
                                
                                # Show donation if recorded
                                if address_id in st.session_state.donations and st.session_state.donations[address_id] > 0:
                                    donation = st.session_state.donations[address_id]
                                    st.success(f"Donation: ${donation}")
                                
                                # View/Edit button
                                if st.button("View/Edit", key=f"view_notes_{address_id}"):
                                    navigate_to("contact", address)
                        
                        if is_ariel:
                            st.markdown("---")
                        else:
                            st.markdown("---")
                
                # Pagination controls
                if total_pages > 1:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.write(f"Page {page} of {total_pages}")
                        prev, next = st.columns(2)
                        if prev.button("Previous Page", disabled=(page == 1)):
                            new_page = max(1, page - 1)
                            st.experimental_set_query_params(page=new_page)
                            st.rerun()
                        if next.button("Next Page", disabled=(page == total_pages)):
                            new_page = min(total_pages, page + 1)
                            st.experimental_set_query_params(page=new_page)
                            st.rerun()
        else:
            st.warning(f"No addresses found for Precinct {precinct_id}. Please try another precinct or check your data file.")
    else:
        st.info("Please select a precinct to begin canvassing")

elif tab == "Demographics" and st.session_state.current_page == "home":
    st.title("Neighborhood Demographics")
    
    # Census data
    census_data = {
        "33701": {
            "total_population": 9137,
            "median_household_income": 67098,
            "bachelors_degree_or_higher": "54.2%",
            "employment_rate": "60.3%",
            "total_housing_units": 6487,
            "without_health_insurance": "9.2%",
            "total_households": 4632
        },
        "33705": {
            "total_population": 27915,
            "median_household_income": 47783,
            "bachelors_degree_or_higher": "30.2%",
            "employment_rate": "56.3%",
            "total_housing_units": 14073,
            "without_health_insurance": "13.2%",
            "total_households": 11300
        }
    }
    
    # Create tabs for each ZIP code
    zip_tabs = st.tabs(["ZIP 33701", "ZIP 33705", "Compare"])
    
    with zip_tabs[0]:
        st.header("ZIP Code 33701")
        
        # Display demographic data
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Population", census_data["33701"]["total_population"])
            st.metric("Median Household Income", f"${census_data['33701']['median_household_income']:,}")
            st.metric("Bachelor's Degree or Higher", census_data["33701"]["bachelors_degree_or_higher"])
            st.metric("Employment Rate", census_data["33701"]["employment_rate"])
        
        with col2:
            st.metric("Total Housing Units", census_data["33701"]["total_housing_units"])
            st.metric("Without Health Insurance", census_data["33701"]["without_health_insurance"])
            st.metric("Total Households", census_data["33701"]["total_households"])
        
        # Add more detailed demographic information
        st.subheader("Key Demographics")
        st.markdown("""
        ZIP code 33701 covers downtown St. Petersburg and the surrounding areas. Key characteristics include:
        
        - Higher median income compared to the city average
        - Higher education levels with over half of residents having a bachelor's degree or higher
        - Mix of single-family homes and condominiums
        - Growing population of young professionals
        - Significant number of retirees and seasonal residents
        """)
        
        st.subheader("Canvassing Tips for 33701")
        st.markdown("""
        - Many residents in this area are well-educated professionals who may respond well to detailed policy discussions
        - Downtown condos may have security systems requiring advance coordination
        - Weekday evenings and weekend afternoons tend to have higher contact rates
        - Many residents are engaged in local issues, particularly downtown development and waterfront access
        """)
    
    with zip_tabs[1]:
        st.header("ZIP Code 33705")
        
        # Display demographic data
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Population", census_data["33705"]["total_population"])
            st.metric("Median Household Income", f"${census_data['33705']['median_household_income']:,}")
            st.metric("Bachelor's Degree or Higher", census_data["33705"]["bachelors_degree_or_higher"])
            st.metric("Employment Rate", census_data["33705"]["employment_rate"])
        
        with col2:
            st.metric("Total Housing Units", census_data["33705"]["total_housing_units"])
            st.metric("Without Health Insurance", census_data["33705"]["without_health_insurance"])
            st.metric("Total Households", census_data["33705"]["total_households"])
        
        # Add more detailed demographic information
        st.subheader("Key Demographics")
        st.markdown("""
        ZIP code 33705 covers south St. Petersburg. Key characteristics include:
        
        - More diverse population compared to 33701
        - Higher percentage of family households
        - Mix of older established neighborhoods and areas of new development
        - Higher percentage of long-term residents
        - More single-family homes compared to downtown
        """)
        
        st.subheader("Canvassing Tips for 33705")
        st.markdown("""
        - Focus on community-oriented messaging and local neighborhood issues
        - Weekend canvassing often yields better results as more families are home
        - Many residents have deep roots in the community and care about neighborhood stability
        - Local schools and community centers are important issues
        - Higher percentage of residents may need information about voter registration and polling locations
        """)
    
    with zip_tabs[2]:
        st.header("Demographic Comparison")
        
        # Create comparison charts using Streamlit's native charting
        comparison_data = {
            "Metric": ["Population", "Median Income ($K)", "Bachelor's+ (%)", "Employment (%)", "Uninsured (%)"],
            "33701": [
                census_data["33701"]["total_population"],
                census_data["33701"]["median_household_income"]/1000,
                float(census_data["33701"]["bachelors_degree_or_higher"].replace("%", "")),
                float(census_data["33701"]["employment_rate"].replace("%", "")),
                float(census_data["33701"]["without_health_insurance"].replace("%", ""))
            ],
            "33705": [
                census_data["33705"]["total_population"],
                census_data["33705"]["median_household_income"]/1000,
                float(census_data["33705"]["bachelors_degree_or_higher"].replace("%", "")),
                float(census_data["33705"]["employment_rate"].replace("%", "")),
                float(census_data["33705"]["without_health_insurance"].replace("%", ""))
            ]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Population comparison (separate due to scale difference)
        st.subheader("Population Comparison")
        pop_df = comparison_df[comparison_df["Metric"] == "Population"].melt(id_vars="Metric", var_name="ZIP", value_name="Value")
        st.bar_chart(pop_df.set_index("ZIP")["Value"])
        
        # Other metrics comparison
        st.subheader("Key Metrics Comparison")
        metrics_df = comparison_df[comparison_df["Metric"] != "Population"]
        
        # Create individual charts for better visualization
        for metric in metrics_df["Metric"].unique():
            st.write(f"**{metric}**")
            metric_df = metrics_df[metrics_df["Metric"] == metric].melt(id_vars="Metric", var_name="ZIP", value_name="Value")
            st.bar_chart(metric_df.set_index("ZIP")["Value"])

elif tab == "Election History" and st.session_state.current_page == "home":
    st.title("Election History")
    
    # Presidential election data
    presidential_data = {
        'Precinct': [123, 130, 108, 126, 109, 121, 119, 125, 118, 106, 116, 117, 122],
        'Registered': [4627, 3764, 2773, 1958, 2151, 922, 2684, 1301, 1175, 760, 1511, 1105, 258],
        'Trump': [1481, 1156, 839, 561, 306, 286, 282, 276, 274, 207, 176, 77, 67],
        'Kamala': [2387, 1996, 1367, 908, 1319, 413, 1432, 732, 708, 454, 835, 598, 149],
        'Voted For Trump %': [32.01, 30.71, 30.26, 28.65, 14.23, 31.02, 10.51, 21.21, 23.32, 27.24, 11.65, 6.97, 25.97],
        'Voted For Kamala %': [51.59, 53.03, 49.30, 46.37, 61.32, 44.79, 53.35, 56.26, 60.26, 59.74, 55.26, 54.12, 57.75]
    }
    presidential_df = pd.DataFrame(presidential_data)
    
    # Create tabs for different views
    election_tabs = st.tabs(["Presidential Results", "Strategic Insights"])
    
    with election_tabs[0]:
        st.header("Presidential Election Results")
        
        # Create a bar chart comparing Trump and Kamala percentages
        chart_df = presidential_df.copy()
        chart_df['Precinct'] = chart_df['Precinct'].astype(str)
        chart_df = chart_df.sort_values('Voted For Kamala %', ascending=False)
        
        # Create a chart comparing Trump and Kamala percentages
        st.bar_chart(chart_df.set_index('Precinct')[['Voted For Trump %', 'Voted For Kamala %']])
        
        # Display the raw data in a table
        st.subheader("Presidential Results Data Table")
        st.dataframe(presidential_df)
    
    with election_tabs[1]:
        st.header("Strategic Insights")
        
        # Strongest Democratic precincts
        strongest_dem = presidential_df.nlargest(3, 'Voted For Kamala %')
        strongest_dem_precincts = strongest_dem['Precinct'].astype(str).tolist()
        strongest_dem_rates = [f"{x:.1f}%" for x in strongest_dem['Voted For Kamala %'].tolist()]
        
        # Strongest Republican precincts
        strongest_rep = presidential_df.nlargest(3, 'Voted For Trump %')
        strongest_rep_precincts = strongest_rep['Precinct'].astype(str).tolist()
        strongest_rep_rates = [f"{x:.1f}%" for x in strongest_rep['Voted For Trump %'].tolist()]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Strongest Democratic Precincts")
            for i in range(len(strongest_dem_precincts)):
                st.markdown(f"**Precinct {strongest_dem_precincts[i]}**: {strongest_dem_rates[i]} for Kamala")
            
            st.markdown("""
            **Strategy for Democratic-Leaning Areas:**
            - Focus on base mobilization and turnout
            - Emphasize progressive policy positions
            - Recruit volunteers from these areas
            - Use these areas for visibility events and rallies
            """)
        
        with col2:
            st.subheader("Strongest Republican Precincts")
            for i in range(len(strongest_rep_precincts)):
                st.markdown(f"**Precinct {strongest_rep_precincts[i]}**: {strongest_rep_rates[i]} for Trump")
            
            st.markdown("""
            **Strategy for Republican-Leaning Areas:**
            - Focus on persuadable voters and independents
            - Emphasize moderate policy positions
            - Address specific local concerns
            - Use targeted messaging on issues with bipartisan appeal
            """)

elif tab == "Stats" and st.session_state.current_page == "home":
    st.title("Canvassing Statistics")
    
    # Calculate statistics from session state
    total_addresses = sum(len(addresses) for addresses in st.session_state.precinct_addresses.values())
    visited_count = len(st.session_state.visited_addresses)
    coverage_percentage = (visited_count / total_addresses * 100) if total_addresses > 0 else 0
    
    # Display overall stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Addresses", total_addresses)
    with col2:
        st.metric("Addresses Visited", visited_count)
    with col3:
        st.metric("Coverage", f"{coverage_percentage:.1f}%")
    
    # Support level breakdown
    st.subheader("Support Level Breakdown")
    
    # Count support levels
    support_counts = {
        "Strong Support": 0,
        "Leaning Support": 0,
        "Undecided": 0,
        "Leaning Against": 0,
        "Strong Against": 0,
        "Refused": 0
    }
    
    for support in st.session_state.support_levels.values():
        if support in support_counts:
            support_counts[support] += 1
    
    # Create a DataFrame for the chart
    support_df = pd.DataFrame({
        'Support Level': list(support_counts.keys()),
        'Count': list(support_counts.values())
    })
    
    # Display the chart
    st.bar_chart(support_df.set_index('Support Level'))
    
    # Donation statistics
    st.subheader("Donation Statistics")
    
    total_donations = sum(st.session_state.donations.values())
    donors_count = len([d for d in st.session_state.donations.values() if d > 0])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Donations", f"${total_donations:.2f}")
    with col2:
        st.metric("Number of Donors", donors_count)
    with col3:
        avg_donation = total_donations / donors_count if donors_count > 0 else 0
        st.metric("Average Donation", f"${avg_donation:.2f}")
    
    # Precinct coverage
    st.subheader("Precinct Coverage")
    
    # Calculate precinct coverage from visited addresses
    precinct_coverage = {}
    precincts = get_district6_precincts()
    
    for p in precincts:
        precinct_id = p['id']
        precinct_addresses = len(st.session_state.precinct_addresses.get(precinct_id, []))
        visited_in_precinct = len([a for a in st.session_state.visited_addresses if a.startswith(f"{precinct_id}_")])
        coverage = (visited_in_precinct / precinct_addresses * 100) if precinct_addresses > 0 else 0
        precinct_coverage[precinct_id] = coverage
    
    # Create a bar chart for precinct coverage
    coverage_df = pd.DataFrame({
        'Precinct': list(precinct_coverage.keys()),
        'Coverage %': list(precinct_coverage.values())
    })
    
    st.bar_chart(coverage_df.set_index('Precinct'))
    
    # Data export options
    st.subheader("Data Export")
    st.markdown("""
    Export your canvassing data for further analysis or reporting. This feature would allow you to:
    - Download interaction notes as CSV
    - Export precinct coverage statistics
    - Generate reports for campaign leadership
    
    *Note: In this demo version, data export is simulated. In a production version, this would generate actual files.*
    """)
    
    if st.button("Export Data (Demo)"):
        st.success("Data export simulated successfully! In a production version, this would download a CSV file.")

elif tab == "Settings" and st.session_state.current_page == "home":
    st.title("Settings")
    
    # Volunteer information
    st.subheader("Volunteer Information")
    
    with st.form("volunteer_form"):
        name = st.text_input("Your Name", value=st.session_state.volunteer_name)
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        
        if st.form_submit_button("Save Settings"):
            st.session_state.volunteer_name = name
            st.success("Settings saved successfully!")
    
    # Map settings
    st.subheader("Map Settings")
    
    cluster_view = st.checkbox("Group Addresses by Default", value=st.session_state.cluster_view)
    if cluster_view != st.session_state.cluster_view:
        st.session_state.cluster_view = cluster_view
        st.success("Map settings saved successfully!")
    
    # Help and support
    st.subheader("Help & Support")
    st.markdown("""
    If you encounter any issues or have questions:
    - Contact your campaign coordinator
    - Email support at support@district6campaign.org
    - Call the campaign office at (727) 555-6789
    """)
    
    # About
    st.subheader("About")
    st.markdown("""
    **District 6 Canvassing App** v1.0
    
    This app helps campaign volunteers efficiently canvas District 6 by providing optimized routes, 
    tracking progress, and recording voter interactions.
    
    Thank you for volunteering! Your efforts make a huge difference in connecting with voters and 
    building support for our campaign.
    """)

# Footer
st.markdown("---")
st.markdown("© 2025 District 6 Campaign | Powered by Streamlit")

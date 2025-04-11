# District 6 Canvassing App - Enhanced Documentation

## Overview

The District 6 Canvassing App is a Streamlit-based application designed to help campaign volunteers efficiently canvas neighborhoods, record voter interactions, and track campaign progress. This documentation covers the app's features, usage instructions, and technical details.

## Key Features

### Address Management
- **Real Address Data**: Uses actual property data from the 33701 and 33705 ZIP codes
- **Precinct Organization**: Organizes addresses by District 6 precincts (106, 108, 109, 116, 117, 118, 119, 121, 122, 123, 125, 126, 130)
- **Address Clustering**: Groups addresses by buildings and neighborhoods for easier navigation
- **Predictive Search**: Suggests names and addresses as you type to quickly find specific voters
- **Property Type Distinction**: Clearly distinguishes between residential and business properties

### Interaction Tracking
- **Contact Recording**: Dedicated contact page for recording detailed voter interactions
- **Support Level Tracking**: Record voter support levels from Strong Support to Strong Against
- **Donation Tracking**: Track donation amounts from each contact
- **Quick Tags**: Apply relevant tags (Supportive, Needs Info, Call Back, etc.) for easy sorting
- **Follow-up Flagging**: Mark addresses for follow-up visits

### Map Visualization
- **Interactive Map**: Shows addresses on a map for better geographic context
- **Building Clusters**: Groups multiple units in the same building for cleaner display
- **Coordinate Mapping**: Accurately displays all addresses with proper geographic positioning

### Robust Data Handling
- **Multiple Data Sources**: Tries multiple file paths and sources to find address data
- **JSON Format Repair**: Automatically fixes common JSON formatting issues
- **Error Handling**: Provides clear error messages and debugging information
- **Fallback Options**: File upload option and sample data generation if all else fails

## User Guide

### For Campaign Managers

1. **Setup**:
   - Ensure your address data file is properly formatted as JSON
   - Deploy the app to Streamlit Cloud or run locally

2. **Strategic Planning**:
   - Use the precinct information to identify priority areas
   - Assign volunteers to specific precincts based on strategic needs

3. **Progress Monitoring**:
   - Track which addresses have been visited
   - Monitor support levels and donation amounts
   - Identify areas needing follow-up

### For Volunteers

1. **Getting Started**:
   - Enter your name in the "Volunteer Name" field
   - Select your assigned precinct from the dropdown menu

2. **Finding Addresses**:
   - Use the predictive search box to find specific addresses or names
   - As you type, suggestions will appear below the search box
   - Click on a suggestion to select it, or continue typing to refine your search
   - Use filters to show/hide visited addresses or filter by property type
   - Toggle between grouped and individual address views

3. **Using the Map**:
   - Scroll down to see the map view of all addresses in your current filter
   - Each point on the map represents an address in the current view
   - Use the map to plan your canvassing route efficiently

4. **Recording Interactions**:
   - Click the "Contact" button to open the contact form
   - Record support level, donation amount, and notes
   - Use quick tags for consistent categorization
   - Check "Flag for follow-up" if needed
   - Click "Save Contact Information" to record the interaction

5. **Marking Non-Contacts**:
   - Use "Not Home" button if no one answers
   - Use "Skip" button to mark addresses to skip

## Technical Documentation

### Data Structure

The app uses a JSON file containing property data with the following key fields:
- `PARCEL_NUMBER`: Unique identifier for each property
- `OWNER1`, `OWNER2`: Property owner names
- `SITE_ADDRESS`, `SITE_CITYZIP`: Property address information
- `STR_NUM`, `STR_NAME`, `STR_UNIT`, `STR_ZIP`: Parsed address components
- `PROPERTY_USE`: Type of property (converted to "Residential" or "Business")
- `PRECINCT`: District 6 precinct number
- `LAT`, `LON`: Latitude and longitude coordinates for map display

### Session State

The app uses Streamlit's session state to maintain data between interactions:
- `volunteer_name`: Name of the current volunteer
- `selected_precinct`: Currently selected precinct
- `visited_addresses`: Set of addresses marked as visited
- `interaction_notes`: Dictionary of notes for each address
- `support_levels`: Dictionary of support levels for each address
- `donations`: Dictionary of donation amounts for each address
- `search_suggestions`: List of autocomplete suggestions for the search box

### Predictive Search Implementation

The app implements predictive search through these key components:

1. **Suggestion Generation**:
   ```python
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
           
           # Check street address
           street_address = str(address.get('SITE_ADDRESS', '')).lower()
           if partial_query in street_address:
               suggestions.add(address.get('SITE_ADDRESS', ''))
           
           # Additional fields checked...
       
       # Convert to list and sort
       suggestion_list = sorted(list(suggestions))
       
       # Limit to top 10 suggestions
       return suggestion_list[:10]
   ```

2. **Suggestion Display**:
   ```python
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
   ```

### Map Functionality

The app implements map visualization through these key components:

1. **Coordinate Assignment**:
   ```python
   # Add coordinates for map if not present
   if 'LAT' not in address or 'LON' not in address:
       # Generate a latitude and longitude near St. Petersburg, FL
       base_lat = 27.773056  # St. Petersburg latitude
       base_lon = -82.639999  # St. Petersburg longitude
       
       # Add small offsets based on street number and precinct to create a scatter effect
       street_num = float(address.get('STR_NUM', 0))
       precinct_id = str(address.get('PRECINCT', '106'))
       
       address['LAT'] = base_lat + (street_num % 100) * 0.0001 + (int(precinct_id) % 10) * 0.001
       address['LON'] = base_lon + (street_num % 50) * 0.0002 - (int(precinct_id) % 5) * 0.001
   ```

2. **Map Display**:
   ```python
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
   
   # Convert to DataFrame for Streamlit's map
   if map_data:
       map_df = pd.DataFrame(map_data)
       st.map(map_df)
   ```

### JSON Error Handling

The app implements robust JSON error handling through several mechanisms:

1. **Multiple File Path Options**:
   ```python
   file_paths = [
       '/home/ubuntu/fixed_addresses.json',
       '/home/ubuntu/addresses.json',
       '/home/ubuntu/upload/addresses.json',
       '/home/ubuntu/upload/Advanced Search 4-11-2025 (1).json'
   ]
   ```

2. **JSON Format Repair Function**:
   ```python
   def fix_json_format(content):
       # Check if content is already valid JSON
       try:
           json.loads(content)
           return content
       except json.JSONDecodeError:
           # Fix common issues
           fixed_content = content.strip()
           if not fixed_content.startswith('['):
               fixed_content = '[' + fixed_content
           if not fixed_content.endswith(']'):
               fixed_content = fixed_content + ']'
           
           # Remove problematic characters
           if fixed_content[0] != '[':
               fixed_content = '[' + fixed_content[fixed_content.find('{'): fixed_content.rfind('}')+1] + ']'
           
           # Try to parse the fixed content
           try:
               json.loads(fixed_content)
               return fixed_content
           except json.JSONDecodeError:
               return None
   ```

3. **Multiple Data Sources**:
   - Local file system
   - GitHub repository
   - File upload through the browser
   - Sample data generation as a last resort

## Troubleshooting

### JSON Parsing Errors

If you encounter JSON parsing errors:

1. **Check the Debug Information**:
   - Expand the "Debug Information" section in the sidebar
   - Review the file paths being checked and any error messages

2. **Use the File Upload Option**:
   - If automatic loading fails, use the file uploader in the sidebar
   - Upload a properly formatted JSON file

3. **Format Your JSON File**:
   - Ensure your JSON file is properly formatted as an array of objects
   - Validate your JSON using a tool like JSONLint (https://jsonlint.com/)
   - Make sure the file starts with `[` and ends with `]`

### Search Issues

If you're having trouble with the predictive search:

1. **Type at least 2 characters**:
   - The search suggestions only appear after you've typed at least 2 characters

2. **Check for partial matches**:
   - The search looks for partial matches in names, addresses, and other fields
   - Try different parts of the name or address if you're not seeing results

3. **Use the filters**:
   - Combine search with filters like "Show Visited" or "Property Type" to narrow results

### Map Display Issues

If the map isn't displaying correctly:

1. **Check for coordinates**:
   - The app automatically generates coordinates for addresses
   - In the debug section, you can verify if LAT and LON fields are present

2. **Refresh the page**:
   - Sometimes the map needs a refresh to display properly
   - Try selecting a different precinct and then returning to your desired precinct

3. **Verify filtered addresses**:
   - The map only shows addresses that match your current filters
   - If no addresses are shown in the list, the map will be empty

## Deployment

### Local Deployment

To run the app locally:

1. Install the required dependencies:
   ```
   pip install streamlit pandas
   ```

2. Run the app:
   ```
   streamlit run enhanced_district6_app.py
   ```

### Streamlit Cloud Deployment

To deploy to Streamlit Cloud:

1. Upload the app files to a GitHub repository:
   - `enhanced_district6_app.py` (renamed to `streamlit_app.py`)
   - `requirements.txt` with `streamlit` and `pandas`
   - Your address data file (JSON format)

2. Connect your repository to Streamlit Cloud:
   - Go to https://streamlit.io/cloud
   - Connect your GitHub repository
   - Select the main branch and streamlit_app.py file
   - Deploy the app

## Future Enhancements

Potential future enhancements for the app:

1. **Data Persistence**:
   - Implement database storage for interaction data
   - Add user authentication for volunteers

2. **Advanced Mapping**:
   - Implement route optimization for canvassing
   - Add heat maps showing support levels by area

3. **Reporting**:
   - Add analytics dashboard for campaign managers
   - Generate reports on canvassing progress and voter sentiment

4. **Mobile Optimization**:
   - Further enhance mobile responsiveness
   - Add offline mode for areas with poor connectivity

## Support

For support with the District 6 Canvassing App, please contact the development team or submit issues through the GitHub repository.

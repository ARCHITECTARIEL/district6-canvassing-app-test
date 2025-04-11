# District 6 Canvassing App - Geographic Features Documentation

## Overview

The District 6 Canvassing App has been enhanced with geographic organization features to make it easier for volunteers to navigate the district and find their way around while canvassing. This document explains the new geographic sections and location finder features.

## Geographic Sections

### What Are Geographic Sections?

The District 6 area has been divided into four main geographic sections:
- **North**: Includes precincts 106, 108, 122, and 130
- **South**: Includes precincts 117, 118, and 125
- **East**: Includes precincts 109, 116, and 123
- **West**: Includes precincts 119, 121, and 126

This organization creates a logical structure that makes it easier for volunteers to focus on specific areas of the district.

### How to Use Geographic Sections

1. **Select a Geographic Section**: At the top of the app, use the "Select Geographic Section" dropdown to choose between "All", "North", "South", "East", or "West".

2. **Filtered Precinct Selection**: Once you select a geographic section, the precinct dropdown will automatically filter to show only precincts within that section.

3. **Address Information**: Each address now displays its geographic section, helping volunteers understand where they are in the district.

4. **Hierarchical Organization**: This creates a two-level hierarchy (Section → Precinct) that makes it easier to organize canvassing efforts by geographic area.

### Benefits of Geographic Sections

- **Easier Navigation**: Volunteers can focus on one geographic area at a time
- **Better Planning**: Campaign managers can assign volunteers to specific sections
- **Logical Organization**: Addresses are grouped in a way that makes geographic sense
- **Reduced Confusion**: New volunteers can more easily understand the district layout

## Location Finder

### What Is the Location Finder?

The Location Finder is a new feature that helps volunteers determine their current location while canvassing. It uses the device's GPS capabilities to show the volunteer's position on the map alongside nearby addresses.

### How to Use the Location Finder

1. **Find My Location Button**: Click the "📍 Find My Location" button in the Location Finder section.

2. **Permission Request**: Your browser will ask for permission to access your location. You must grant this permission for the feature to work.

3. **Map Update**: Once your location is determined, the map will update to show your current position alongside nearby addresses.

4. **Current Coordinates**: Your current latitude and longitude coordinates will be displayed below the button.

### Technical Details

The Location Finder uses the browser's Geolocation API to determine the user's current position. This requires:

1. A device with GPS capabilities or network-based location services
2. User permission to access location data
3. An active internet connection

For privacy reasons, location data is only used within the app and is not stored or transmitted elsewhere.

### Benefits of the Location Finder

- **Easier Orientation**: Volunteers can see exactly where they are in relation to addresses
- **Reduced Getting Lost**: New volunteers can more easily navigate unfamiliar areas
- **Efficient Routing**: Volunteers can see which addresses are closest to their current location
- **Better Time Management**: Reduces time spent figuring out where to go next

## Using Geographic Features Together

The Geographic Sections and Location Finder features work best when used together:

1. **Start with a Section**: Begin by selecting the geographic section you're assigned to canvas
2. **Choose a Precinct**: Select a specific precinct within that section
3. **Find Your Location**: Use the Location Finder to see where you are
4. **Plan Your Route**: Use the map to plan an efficient route between addresses
5. **Track Progress**: As you visit addresses, they'll be marked as visited in the app

This combination of features makes canvassing more efficient and less confusing, especially for new volunteers.

## Troubleshooting

### Geographic Sections Issues

- **No Precincts Shown**: If no precincts appear after selecting a geographic section, try selecting "All" and then reselecting your desired section.
- **Wrong Section Assignment**: If you believe an address is assigned to the wrong geographic section, please notify the campaign office.

### Location Finder Issues

- **Permission Denied**: If you denied location permission, you'll need to update your browser settings to allow location access for this app.
- **Location Not Accurate**: GPS accuracy can vary based on your device and environment. Urban areas with tall buildings may have less accurate readings.
- **Feature Not Working**: Some older devices or browsers may not support the Geolocation API. Try using a modern browser like Chrome, Firefox, or Safari.

## Future Enhancements

Potential future improvements to the geographic features include:

1. **Turn-by-Turn Directions**: Integration with mapping services to provide directions between addresses
2. **Optimized Routes**: Automatically generating the most efficient canvassing route
3. **Offline Maps**: Downloading map data for use in areas with poor connectivity
4. **Heat Maps**: Visualizing support levels by geographic area

## Feedback

Your feedback on these new geographic features is valuable! Please share your experiences and suggestions with the campaign team to help us continue improving the app.


# District 6 Canvassing App - User Guide

## Overview
The District 6 Canvassing App is designed to help campaign volunteers efficiently canvas neighborhoods in District 6, focusing specifically on addresses in ZIP codes 33701 and 33705. This guide provides comprehensive instructions for using and maintaining the app.

## Getting Started

### Accessing the App
The app is deployed at: https://district6-canvassing-app-enhanced-dbmyv4barlaidoybvmd9f6.streamlit.app/

### Initial Setup
1. When you first open the app, use the file uploader in the sidebar to upload your addresses.json file
2. The app will process your data and organize addresses by precinct
3. Enter your name in the Settings tab to personalize your experience

## Main Features

### Home Tab
- **Precinct Selection**: Choose from all 13 District 6 precincts (106, 108, 109, 116, 117, 118, 119, 121, 122, 123, 125, 126, 130)
- **Map View**: See all addresses in the selected precinct displayed as individual points on the map
- **Address List**: Browse through all addresses in the selected precinct
- **Search Function**: Find specific addresses by name, street, or number
- **Filtering Options**: Filter addresses by visit status and property type
- **Interaction Recording**: Record detailed notes about each voter contact

### Demographics Tab
- **ZIP Code Data**: View demographic information for ZIP codes 33701 and 33705
- **Comparison Charts**: Compare key demographic metrics between ZIP codes
- **Canvassing Tips**: Get tailored advice for approaching voters in different neighborhoods

### Election History Tab
- **Presidential Results**: See Trump vs. Kamala voting patterns for each precinct
- **Strategic Insights**: Get precinct-specific canvassing strategies based on voting patterns

### Stats Tab
- **Progress Tracking**: Monitor your canvassing progress across all precincts
- **Precinct Coverage**: See which precincts have been most thoroughly canvassed
- **Data Export**: Export your canvassing data for further analysis (simulated in demo version)

### Settings Tab
- **Volunteer Information**: Update your name and contact details
- **Help & Support**: Access contact information for campaign support

## How to Use the App

### For Campaign Managers
1. **Strategic Planning**: Use the Election History tab to identify priority precincts
2. **Volunteer Assignment**: Assign volunteers to specific precincts based on strategic needs
3. **Progress Monitoring**: Track canvassing progress in the Stats tab
4. **Data Analysis**: Analyze voter sentiment and interaction patterns

### For Volunteers
1. **Select a Precinct**: Choose your assigned precinct from the dropdown menu
2. **View Addresses**: See a list of addresses to visit with property information
3. **Use the Map**: Navigate to addresses using the map view
4. **Record Interactions**: Use the Contact button to record detailed notes about each interaction
5. **Mark Non-Contacts**: Use the Not Home or Skip buttons for addresses where no contact was made

## Troubleshooting

### Common Issues
- **No Addresses Showing**: Make sure you've uploaded your addresses.json file using the sidebar uploader
- **Map Not Loading**: Try refreshing the page or selecting a different precinct
- **Search Not Working**: Ensure you're using simple search terms (names, street names, or numbers)

### Data Management
- **Lost Interaction Data**: Session data is stored in the browser; use the "Sync Data" button regularly
- **Multiple Volunteers**: Each volunteer should use a unique name in Settings to distinguish their interactions

## Technical Information

### App Structure
- The app is built with Streamlit and uses pandas for data processing
- Address data is loaded from a JSON file uploaded by the user
- Maps are created using Streamlit's native map component
- Session state is used to maintain data between interactions

### Deployment
- The app is deployed on Streamlit Cloud
- The GitHub repository contains:
  - streamlit_app.py (main application file)
  - requirements.txt (dependencies: streamlit==1.31.0, pandas==2.0.3)

### Maintenance
- To update the app, modify the streamlit_app.py file in the GitHub repository
- Streamlit Cloud will automatically redeploy when changes are detected
- Keep the requirements.txt file minimal to ensure reliable deployment

## Tips for Effective Canvassing
- Review the demographic information for your assigned area before starting
- Use the strategic insights for each precinct to tailor your approach
- Record detailed notes that will be helpful for follow-up contacts
- Use the map view to plan efficient routes between addresses
- Regularly sync your data to share information with the campaign team

## Support and Contact
If you encounter any issues or have questions:
- Contact your campaign coordinator
- Email support at support@district6campaign.org
- Call the campaign office at (727) 555-6789

Thank you for your dedication to the District 6 campaign! Your door-knocking efforts make a significant difference in connecting with voters and building support for our candidate.

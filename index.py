from flask import Flask, jsonify, request
from bs4 import BeautifulSoup
import requests
from datetime import datetime
from urllib.parse import unquote,urlparse, parse_qs

app = Flask(__name__)

def scrape_skillrack_profile(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Initialize variables for the profile data
    profile_data = {
        'id': '',
        'name': '',
        'dept': '',
        'year': '',
        'college': '',
        'code_tutor': 0,
        'code_track': 0,
        'code_test': 0,
        'dt': 0,
        'dc': 0,
        'points': 0,
        'required_points': 0,
        'deadline': None,
        'percentage': 100,
        'last_fetched': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'url': url
    }

    # Extract profile ID from the URL
    parsed_url = urlparse(url)
    profile_data['id'] = parse_qs(parsed_url.query).get('id', [None])[0]

    # Extract the name
    name_div = soup.find('div', {'class': 'ui big label black'})  # Verify this selector
    if name_div:
        profile_data['name'] = name_div.text.strip()

    # Extract department, year, and college
    profile_div = soup.find('div', {'class': 'ui four wide center aligned column'})  # Verify this selector
    if profile_div:
        raw_text = profile_div.text.strip().split('\n')
        if len(raw_text) > 8:  # Ensure the expected structure exists
            profile_data['dept'] = raw_text[4].strip()
            profile_data['college'] = raw_text[6].strip()
            profile_data['year'] = raw_text[8].strip()[-4:]  # Last 4 digits as year

    # Extract statistics
    statistics_div = soup.find_all('div', class_='statistic')
    labels_to_extract = {
        'CODE TUTOR': 'code_tutor',
        'CODE TEST': 'code_test',
        'CODE TRACK': 'code_track',
        'DC': 'dc',
        'DT': 'dt',
        'Points': 'points',
        'Required Points': 'required_points',
        'Deadline': 'deadline',
        'Percentage': 'percentage'
    }

    for stat in statistics_div:
        label_div = stat.find('div', class_='label')
        if label_div:
            label = label_div.get_text(strip=True)
            if label in labels_to_extract:
                value_div = stat.find('div', class_='value')
                if value_div:
                    value = value_div.get_text(strip=True)
                    if label == 'Percentage':
                        try:
                            profile_data['percentage'] = int(value.replace('%', ''))
                        except ValueError:
                            profile_data['percentage'] = 100
                    elif label == 'Deadline':
                        profile_data['deadline'] = value if value else None
                    else:
                        try:
                            profile_data[labels_to_extract[label]] = int(value)
                        except ValueError:
                            profile_data[labels_to_extract[label]] = value

    return profile_data


# Define the API endpoint to accept a URL in the path
@app.route('/api/points/<path:encoded_url>', methods=['GET'])
def get_points(encoded_url):
    # Decode the URL from the path
    url = unquote(encoded_url)

    # Validate the URL
    if not url.startswith("http"):
        return jsonify({'error': 'Invalid URL provided'}), 400

    # Scrape the data
    data = scrape_skillrack_profile(url)

    # Return the data as a JSON response
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)

# from flask import Flask, jsonify, request
# from bs4 import BeautifulSoup
# import requests
# from datetime import datetime
# from urllib.parse import urlparse, parse_qs

# app = Flask(__name__)

# # Function to scrape data from the given URL
# def scrape_skillrack_data(url):
#     try:
#         # Send a GET request to the Skillrack URL
#         response = requests.get(url)

#         # Parse the response HTML using BeautifulSoup
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Initialize variables for the profile data
#         id = ''
#         name = ''
#         dept = ''
#         year = ''
#         college = ''

#         # Initialize variables for the statistics
#         code_tutor = 0
#         code_track = 0
#         code_test = 0
#         dt = 0
#         dc = 0
#         points = 0
#         required_points = 0
#         deadline = None
#         percentage = 100
#         last_fetched = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Extracting profile data (id, name, dept, year, college)
#         name = soup.find('div', {'class': 'ui big label black'}).text.strip()
#         # Extracting additional data from the profile
#         parsed_url = urlparse(url)
#         id = parse_qs(parsed_url.query).get('id', [None])[0]
#         raw_text = soup.find('div', {'class': 'ui four wide center aligned column'}).text.strip().split('\n')
#         dept = raw_text[4].strip()
#         year = raw_text[8].strip()[-4:]  # Extracting the last 4 digits as year
#         college = raw_text[6].strip()

#         # Find the statistics section where the values are stored
#         statistics_div = soup.find_all('div', class_='statistic')

#         # Define the labels and corresponding keys to be extracted
#         labels_to_extract = {
#             'CODE TUTOR': 'code_tutor',
#             'CODE TEST': 'code_test',
#             'CODE TRACK': 'code_track',
#             'DC': 'dc',
#             'DT': 'dt',
#             'Points': 'points',
#             'Required Points': 'required_points',
#             'Deadline': 'deadline',
#             'Percentage': 'percentage'
#         }

#         # Loop through each statistic div and extract data for the required labels
#         for stat in statistics_div:
#             label_div = stat.find('div', class_='label')
            
#             if label_div:
#                 label = label_div.get_text(strip=True)
                
#                 # Check if the label is in the list of labels we need
#                 if label in labels_to_extract:
#                     value_div = stat.find('div', class_='value')
                    
#                     if value_div:
#                         value = value_div.get_text(strip=True)
                        
#                         # Special handling for percentage and deadline
#                         if label == 'Percentage':
#                             try:
#                                 percentage = int(value.replace('%', ''))
#                             except ValueError:
#                                 percentage = 100  # default if there's an issue with the percentage value
#                         elif label == 'Deadline':
#                             # Handle deadline formatting or leaving it as None if not available
#                             deadline = value if value else None
#                         else:
#                             # Convert other values to integers
#                             try:
#                                 globals()[labels_to_extract[label]] = int(value)
#                             except ValueError:
#                                 globals()[labels_to_extract[label]] = value  # Handle non-integer values like 'None'

#         # Return the collected data as a dictionary
#         return {
#             'id': id,
#             'name': name,
#             'dept': dept,
#             'year': year,
#             'college': college,
#             'code_tutor': code_tutor,
#             'code_track': code_track,
#             'code_test': code_test,
#             'dt': dt,
#             'dc': dc,
#             'points': points,
#             'required_points': required_points,
#             'deadline': deadline,
#             'percentage': percentage,
#             'last_fetched': last_fetched,
#             'url': url
#         }
#     except Exception as e:
#         return {'error': str(e)}

# # Define the API endpoint
# @app.route('/api/points', methods=['GET'])
# def get_points():
#     # Get the full URL from the query parameters
#     url = request.args.get('url')
    
#     if not url:
#         return jsonify({'error': 'URL parameter is required'}), 400

#     # Scrape the data
#     data = scrape_skillrack_data(url)

#     # Return the data as a JSON response
#     return jsonify(data)

# if __name__ == '__main__':
#     app.run(debug=True)

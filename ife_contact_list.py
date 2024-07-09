import os
import requests
import sys
from io import BytesIO
import pandas as pd
from geopy.geocoders import OpenCage
from geopy.distance import geodesic
from pprint import pprint
import diskcache as dc

from openpyxl import load_workbook

# Postcode from env variable or first command line argument which overrides the env variable if set
TARGET_POSTCODE = os.getenv("TARGET_POSTCODE") or (sys.argv[1] if len(sys.argv) > 1 else None)

# Load other environment variables
OPENCAGE_API_KEY = os.getenv('OPENCAGE_API_KEY')
IFE_BASE_URL = os.getenv('IFE_BASE_URL', 'https://www.ife.org.uk/write/MediaUploads/')
FILENAME = os.getenv('FILENAME', 'CEngandIEngUKlisting23.02.24.xlsx')
IFE_URL = IFE_BASE_URL + FILENAME

DIRECTORY = os.getenv('DATA_DIRECTORY', './data/')
# Create a data directory if it doesn't exist
if not os.path.exists(DIRECTORY):
    os.makedirs(DIRECTORY)

local_file_path = DIRECTORY + FILENAME

# Download the file if it doesn't exist, otherwise read it from the file system
if not os.path.exists(local_file_path):
    response = requests.get(IFE_URL)
    response.raise_for_status()  # Ensure the request was successful
    with open(local_file_path, 'wb') as f:
        f.write(response.content)
    xlsx_data = BytesIO(response.content)
else:
    xlsx_data = local_file_path

# Load the XLSX file into a DataFrame
df = pd.read_excel(xlsx_data, skiprows=3)

# Initialize OpenCage Geocoder and DiskCache
geolocator = OpenCage(OPENCAGE_API_KEY)
cache = dc.Cache(DIRECTORY + 'geocode_cache')  # Cache directory

# Function to geocode each address
def geocode_address(row):
    address_parts = [
        row['Town / City'],
        row['County'],
        row['Country']
    ]
    # Filter out NaN values and join remaining parts
    address = ', '.join([str(part) for part in address_parts if pd.notna(part)])
    
    print(f"Geocoding address: {address}")
    
    if address in cache:
        return cache[address]
    
    location = geolocator.geocode(address)
    if location:
        cache[address] = (location.latitude, location.longitude)
        return location.latitude, location.longitude
    
    print(f"Unable to geocode address: {address}")
    return None, None

# Geocode each row
df['Latitude'], df['Longitude'] = zip(*df.apply(geocode_address, axis=1))

# Reorder columns to place "Area of Work" last
columns = [col for col in df.columns if col != 'Area of Work'] + ['Area of Work']
df = df[columns]

# Save to JSON format
json_data = df.to_json(orient='records', indent=4)
print(json_data)

# Print each sorted row using pprint
pprint(df.to_dict(orient='records'))

# Save JSON to a file
json_file_path = DIRECTORY + 'CEngandIEngUKlisting.json'
with open(json_file_path, 'w') as json_file:
    json_file.write(json_data)
print(f"JSON data saved to: {json_file_path}")

# Define the target postcode to calculate distance from
target_location = geolocator.geocode(TARGET_POSTCODE)

if not target_location:
    raise ValueError(f"Unable to find coordinates for the postcode: {TARGET_POSTCODE}")

target_coords = (target_location.latitude, target_location.longitude)

# Function to calculate distance from the target postcode
def calculate_distance(row):
    coords = (row['Latitude'], row['Longitude'])
    if None in coords or pd.isna(coords[0]) or pd.isna(coords[1]):
        return None
    return geodesic(target_coords, coords).miles


# Calculate distances
df['Distance from Target (miles)'] = df.apply(calculate_distance, axis=1)
sorted_df = df.sort_values(by='Distance from Target (miles)', ascending=True)

# Print each sorted row using pprint
pprint(sorted_df.to_dict(orient='records'))

# Save sorted to JSON format
sorted_json_data = sorted_df.to_json(orient='records', indent=4)
print(sorted_json_data)

# Save sorted JSON to a file
json_file_path = DIRECTORY + 'CEngandIEngUKlisting_sorted.json'
with open(json_file_path, 'w') as json_file:
    json_file.write(json_data)
print(f"sorted JSON data saved to: {json_file_path}")

# Save the sorted data back to an XLSX file
sorted_xlsx_path = DIRECTORY + 'CEngandIEngUKlisting_sorted.xlsx'
sorted_df.to_excel(sorted_xlsx_path, index=False)

# Automatically resize columns in the XLSX file
def auto_resize_columns(excel_path):
    workbook = load_workbook(excel_path)
    worksheet = workbook.active
    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter
        for cell in col:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except Exception:
                pass
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column].width = adjusted_width
    workbook.save(excel_path)

# Resize columns
auto_resize_columns(sorted_xlsx_path)

print(f"Sorted XLSX data saved to: {sorted_xlsx_path}")

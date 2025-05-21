# import requests
# import json
# import msal
# import logging
# import pandas as pd
# import time
# from urllib.parse import urlparse, parse_qs

# class GraphAPI:
#     def __init__(self, credentials=None):
#         self.logger = logging.getLogger(__name__)
#         self.credentials = credentials
#         self.access_token = None
#         self.sharepoint_site_id = None
#         self.drive_id = None
#         self.file_id = None
#         self.sheet_name = "Super Player Auction"
        
#         # SharePoint URL for the Excel file
#         self.sharepoint_url = "https://cricbattle.sharepoint.com/:x:/r/sites/CorpDevaaf94619130d4a79af9f3aeae502bdb5/_layouts/15/Doc2.aspx?action=edit&sourcedoc=%7B9e836ed5-f58f-4dc7-a969-3c62b255f3ea%7D"
        
#         # Parse the URL to extract the file ID
#         self.extract_file_id_from_url()
        
#     def extract_file_id_from_url(self):
#         """Extract the file ID from the SharePoint URL"""
#         try:
#             parsed_url = urlparse(self.sharepoint_url)
#             query_params = parse_qs(parsed_url.query)
            
#             if 'sourcedoc' in query_params:
#                 # Extract the file ID from the sourcedoc parameter
#                 file_id = query_params['sourcedoc'][0]
#                 # Remove the curly braces
#                 file_id = file_id.strip('{}')
#                 self.file_id = file_id
#                 self.logger.info(f"Extracted file ID: {self.file_id}")
                
#                 # Extract site from the URL path
#                 path_parts = parsed_url.path.split('/')
#                 site_index = path_parts.index('sites') if 'sites' in path_parts else -1
#                 if site_index >= 0 and len(path_parts) > site_index + 1:
#                     self.sharepoint_site_id = path_parts[site_index + 1]
#                     self.logger.info(f"Extracted site ID: {self.sharepoint_site_id}")
#         except Exception as e:
#             self.logger.error(f"Error extracting file ID from URL: {e}")

#     def authenticate(self):
#         """Authenticate with Microsoft Graph API using MSAL"""
#         try:
#             # Create a confidential client application
#             app = msal.ConfidentialClientApplication(
#                 self.credentials['client_id'],
#                 authority=f"https://login.microsoftonline.com/{self.credentials['tenant_id']}",
#                 client_credential=self.credentials['client_secret']
#             )
            
#             # Acquire token with appropriate scope for Excel operations
#             result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
            
#             if "access_token" in result:
#                 self.access_token = result["access_token"]
#                 self.logger.info("Authentication successful")
#                 return True
#             else:
#                 self.logger.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
#                 return False
#         except Exception as e:
#             self.logger.error(f"Error during authentication: {e}")
#             return False

#     def get_drive_id(self):
#         """Get the drive ID for the SharePoint site"""
#         if not self.access_token or not self.sharepoint_site_id:
#             self.logger.error("Access token or site ID not available")
#             return False
            
#         try:
#             url = f"https://graph.microsoft.com/v1.0/sites/cricbattle.sharepoint.com:/sites/{self.sharepoint_site_id}:/drives"
            
#             headers = {
#                 'Authorization': f'Bearer {self.access_token}',
#                 'Content-Type': 'application/json'
#             }
            
#             response = requests.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 drives = response.json().get('value', [])
#                 if drives:
#                     self.drive_id = drives[0].get('id')
#                     self.logger.info(f"Retrieved drive ID: {self.drive_id}")
#                     return True
#                 else:
#                     self.logger.error("No drives found")
#                     return False
#             else:
#                 self.logger.error(f"Error getting drive ID: {response.status_code}, {response.text}")
#                 return False
#         except Exception as e:
#             self.logger.error(f"Error retrieving drive ID: {e}")
#             return False

#     def get_existing_data(self):
#         """Get existing data from the Excel sheet"""
#         if not all([self.access_token, self.drive_id, self.file_id, self.sheet_name]):
#             self.logger.error("Required parameters not available")
#             return None
            
#         try:
#             url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.sheet_name}/usedRange"
            
#             headers = {
#                 'Authorization': f'Bearer {self.access_token}',
#                 'Content-Type': 'application/json'
#             }
            
#             response = requests.get(url, headers=headers)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 values = data.get('values', [])
                
#                 if not values:
#                     self.logger.warning("No data found in the sheet")
#                     return None
                    
#                 # First row contains headers
#                 headers = values[0]
                
#                 # Convert to a list of dictionaries
#                 rows = []
#                 for i in range(1, len(values)):
#                     row_dict = {}
#                     for j in range(len(headers)):
#                         if j < len(values[i]):
#                             row_dict[headers[j]] = values[i][j]
#                         else:
#                             row_dict[headers[j]] = ""
#                     rows.append(row_dict)
                
#                 self.logger.info(f"Retrieved {len(rows)} rows from Excel")
#                 return rows
#             else:
#                 self.logger.error(f"Error getting sheet data: {response.status_code}, {response.text}")
#                 return None
#         except Exception as e:
#             self.logger.error(f"Error retrieving sheet data: {e}")
#             return None

#     def update_excel(self, new_data):
#         """Update the Excel sheet with new data"""
#         if not self.access_token:
#             if not self.authenticate():
#                 return False
                
#         # Get drive ID if not already available
#         if not self.drive_id:
#             if not self.get_drive_id():
#                 return False
                
#         # Get existing data
#         existing_data = self.get_existing_data()
        
#         if existing_data is None:
#             self.logger.error("Failed to retrieve existing data")
#             return False
            
#         # Get column headers to ensure we have the correct order and all columns
#         url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.sheet_name}/usedRange(valuesOnly=true)"
        
#         headers = {
#             'Authorization': f'Bearer {self.access_token}',
#             'Content-Type': 'application/json'
#         }
        
#         response = requests.get(url, headers=headers)
        
#         if response.status_code != 200:
#             self.logger.error(f"Error getting sheet headers: {response.status_code}, {response.text}")
#             return False
            
#         excel_headers = response.json()['values'][0]
        
#         # Create a lookup of existing tournaments by name to avoid duplicates
#         existing_tournaments = {item.get('Tournament Name', ''): item for item in existing_data}
        
#         # Prepare data to be added (only new tournaments)
#         new_entries = []
#         for tournament in new_data:
#             tournament_name = tournament.get('Tournament Name', '')
#             if tournament_name and tournament_name not in existing_tournaments:
#                 new_entries.append(tournament)
                
#         if not new_entries:
#             self.logger.info("No new tournaments to add")
#             return True
            
#         # Determine the row where we should start appending data
#         start_row = len(existing_data) + 2  # +2 because row 1 is headers and Excel is 1-indexed
        
#         try:
#             # Convert new entries to the format expected by the API
#             # Ensure each row has the same number of columns as the headers
#             values = []
            
#             for entry in new_entries:
#                 row = []
#                 # Make sure we follow the exact column order from Excel
#                 for header in excel_headers:
#                     row.append(entry.get(header, ""))
#                 values.append(row)
                
#             # Create the request
#             range_address = f"A{start_row}:{chr(65 + len(excel_headers) - 1)}{start_row + len(new_entries) - 1}"
#             url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.sheet_name}/range(address='{range_address}')"
            
#             self.logger.info(f"Updating range {range_address} with {len(new_entries)} new entries")
            
#             payload = {
#                 "values": values
#             }
            
#             response = requests.patch(url, headers=headers, data=json.dumps(payload))
            
#             if response.status_code == 200:
#                 self.logger.info(f"Successfully added {len(new_entries)} new tournaments to Excel")
#                 return True
#             else:
#                 self.logger.error(f"Error updating Excel: {response.status_code}, {response.text}")
                
#                 # Log more details for debugging
#                 self.logger.debug(f"Range address: {range_address}")
#                 self.logger.debug(f"Number of rows being inserted: {len(values)}")
#                 self.logger.debug(f"Number of columns per row: {len(values[0]) if values else 0}")
#                 self.logger.debug(f"Expected columns: {len(excel_headers)}")
                
#                 return False
                
#         except Exception as e:
#             self.logger.error(f"Error updating Excel: {e}")
#             return False

import requests
import json
import msal
import logging
import pandas as pd
import time
import os
from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)

class GraphAPI:
    def __init__(self, excel_url, worksheet_name):
        self.excel_url = excel_url
        self.worksheet_name = worksheet_name
        self.access_token = None
        
        # Extract file ID and site ID from Excel URL
        try:
            # Example URL format: https://corpdev.sharepoint.com/sites/yoursite/Shared%20Documents/General/your_file.xlsx
            parts = self.excel_url.split('/')
            file_name_with_extension = parts[-1]
            self.file_id = file_name_with_extension.split('.')[0]  # This might need adjustment based on your actual file ID
            site_index = parts.index('sites')
            self.site_id = parts[site_index + 1]
            
            logger.info(f"Extracted file ID: {self.file_id}")
            logger.info(f"Extracted site ID: {self.site_id}")
        except Exception as e:
            logger.error(f"Error extracting file and site IDs: {e}")
            raise

    def authenticate(self):
        """Authenticate with Microsoft Graph API"""
        try:
            # Load credentials from environment variables or file
            client_id = os.environ.get('AZURE_CLIENT_ID')
            tenant_id = os.environ.get('AZURE_TENANT_ID')
            client_secret = os.environ.get('AZURE_CLIENT_SECRET')
            
            # If environment variables are not set, try to load from file
            if not (client_id and tenant_id and client_secret):
                try:
                    with open('id.txt', 'r') as f:
                        cred_data = json.load(f)
                        client_id = cred_data.get('client_id')
                        tenant_id = cred_data.get('tenant_id')
                        client_secret = cred_data.get('client_secret')
                except Exception as e:
                    logger.error(f"Error loading credentials from file: {e}")
                    return False

            # Ensure all credentials are present
            if not (client_id and tenant_id and client_secret):
                logger.error("Missing credentials for Microsoft Graph API")
                return False

            # Initialize MSAL app
            authority = f"https://login.microsoftonline.com/{tenant_id}"
            app = msal.ConfidentialClientApplication(
                client_id,
                authority=authority,
                client_credential=client_secret
            )

            # Get token for Microsoft Graph
            scopes = ["https://graph.microsoft.com/.default"]
            result = app.acquire_token_for_client(scopes=scopes)

            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully authenticated with Microsoft Graph API")
                return True
            else:
                logger.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error during authentication: {e}")
            return False

    def get_drive_id(self):
        """Get the drive ID for the SharePoint site"""
        if not self.access_token or not self.site_id:
            logger.error("Access token or site ID not available")
            return False
            
        try:
            url = f"https://graph.microsoft.com/v1.0/sites/cricbattle.sharepoint.com:/sites/{self.site_id}:/drives"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                drives = response.json().get('value', [])
                if drives:
                    self.drive_id = drives[0].get('id')
                    logger.info(f"Retrieved drive ID: {self.drive_id}")
                    return True
                else:
                    logger.error("No drives found")
                    return False
            else:
                logger.error(f"Error getting drive ID: {response.status_code}, {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error retrieving drive ID: {e}")
            return False

    def get_existing_data(self):
        """Get existing data from the Excel sheet"""
        if not all([self.access_token, self.drive_id, self.file_id, self.worksheet_name]):
            logger.error("Required parameters not available")
            return None
            
        try:
            url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.worksheet_name}/usedRange"
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                values = data.get('values', [])
                
                if not values:
                    logger.warning("No data found in the sheet")
                    return None
                    
                # First row contains headers
                headers = values[0]
                
                # Convert to a list of dictionaries
                rows = []
                for i in range(1, len(values)):
                    row_dict = {}
                    for j in range(len(headers)):
                        if j < len(values[i]):
                            row_dict[headers[j]] = values[i][j]
                        else:
                            row_dict[headers[j]] = ""
                    rows.append(row_dict)
                
                logger.info(f"Retrieved {len(rows)} rows from Excel")
                return rows
            else:
                logger.error(f"Error getting sheet data: {response.status_code}, {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error retrieving sheet data: {e}")
            return None

    def update_excel(self, new_data):
        """Update the Excel sheet with new data"""
        if not self.access_token:
            if not self.authenticate():
                return False
                
        # Get drive ID if not already available
        if not self.drive_id:
            if not self.get_drive_id():
                return False
                
        # Get existing data
        existing_data = self.get_existing_data()
        
        if existing_data is None:
            logger.error("Failed to retrieve existing data")
            return False
            
        # Get column headers to ensure we have the correct order and all columns
        url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.worksheet_name}/usedRange(valuesOnly=true)"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.error(f"Error getting sheet headers: {response.status_code}, {response.text}")
            return False
            
        excel_headers = response.json()['values'][0]
        
        # Create a lookup of existing tournaments by name to avoid duplicates
        existing_tournaments = {item.get('Tournament Name', ''): item for item in existing_data}
        
        # Prepare data to be added (only new tournaments)
        new_entries = []
        for tournament in new_data:
            tournament_name = tournament.get('Tournament Name', '')
            if tournament_name and tournament_name not in existing_tournaments:
                new_entries.append(tournament)
                
        if not new_entries:
            logger.info("No new tournaments to add")
            return True
            
        # Determine the row where we should start appending data
        start_row = len(existing_data) + 2  # +2 because row 1 is headers and Excel is 1-indexed
        
        try:
            # Convert new entries to the format expected by the API
            # Ensure each row has the same number of columns as the headers
            values = []
            
            for entry in new_entries:
                row = []
                # Make sure we follow the exact column order from Excel
                for header in excel_headers:
                    row.append(entry.get(header, ""))
                values.append(row)
                
            # Create the request
            range_address = f"A{start_row}:{chr(65 + len(excel_headers) - 1)}{start_row + len(new_entries) - 1}"
            url = f"https://graph.microsoft.com/v1.0/drives/{self.drive_id}/items/{self.file_id}/workbook/worksheets/{self.worksheet_name}/range(address='{range_address}')"
            
            logger.info(f"Updating range {range_address} with {len(new_entries)} new entries")
            
            payload = {
                "values": values
            }
            
            response = requests.patch(url, headers=headers, data=json.dumps(payload))
            
            if response.status_code == 200:
                logger.info(f"Successfully added {len(new_entries)} new tournaments to Excel")
                return True
            else:
                logger.error(f"Error updating Excel: {response.status_code}, {response.text}")
                
                # Log more details for debugging
                logger.debug(f"Range address: {range_address}")
                logger.debug(f"Number of rows being inserted: {len(values)}")
                logger.debug(f"Number of columns per row: {len(values[0]) if values else 0}")
                logger.debug(f"Expected columns: {len(excel_headers)}")
                
                return False
                
        except Exception as e:
            logger.error(f"Error updating Excel: {e}")
            return False
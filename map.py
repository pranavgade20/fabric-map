import json
import os.path

import time
import flask
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "1tRrLoB87PN0XQ62REsR36_tUo0jqvjqsRSj5ocjLCic"
RANGE_NAME = "Form Responses 1!A2:C"

app = flask.Flask(__name__, template_folder='.')

locs = None
last_updated = 0


def get_locs():
    global locs, last_updated
    if locs is not None and time.time() - last_updated < 60*60*24:
        return locs
    last_updated = time.time()
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "/home/p/Downloads/client_secret_1062805821973-eh2270b0oi3vo0bc955cq8cust56dqid.apps.googleusercontent.com.json",
                SCOPES,

            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        for v in values:
            v[2] = v[2].split("\n")[0]

        locs = values
        return values
    except HttpError as err:
        print(err)

@app.route("/", methods=["GET"])
def get_map():
    return flask.render_template("map.html", locations=json.dumps(get_locs()))

if __name__ == "__main__":
    app.run(debug=True, port=8765, host="0.0.0.0")

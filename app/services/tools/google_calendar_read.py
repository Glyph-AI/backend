import json
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from .base_tool import BaseTool

EVENT_FORMAT = """
NAME: {summary}
ORGANIZER: {creator}
ATTENDEES: {attendees}
START DATE: {start_date}
END DATE: {end_date}
HTML LINK: {link}
LOCATION: {location}
"""


class GoogleCalendarRead(BaseTool):
    def class_init(self):
        self.scope = 'https://www.googleapis.com/auth/calendar.events'
        self.client_id = "520170255321-uve0rbqvotf5v8163d8b5k8b3bfegk88.apps.googleusercontent.com"
        self.client_secret = "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"

    def __internal_query_requires(self):
        return """
        Input must match the following: 
        ```
            {{
                "type": $READ_TYPE,
                "query": $READ_QUERY
            }}
        ```
        $READ_TYPE must be either "daterange" or "search"
        $READ_QUERY must be:
            - a date range, formatted "MM/DD/YYYY - MM/DD/YYYY" if $READ_TYPE is "daterange"
            - a search string, if $READ_TYPE is "search"
        """

    def __parse_message(self, message):
        try:
            json_response = json.loads(message)
            return json_response["type"], json_response["query"]
        except Exception as e:
            print(e, message)
            return None, None

    def __parse_date_range(self, date_range_string: str):
        start, end = date_range_string.split(" - ")
        start_date = datetime.strptime(start, "%m/%d/%y").isoformat()
        end_date = datetime.strptime(end, "%m/%d/%y").isoformat()

        return start_date, end_date

    def __format_person(self, person):
        return f"{person.get('displayName', '')} | {person['email']}"

    def __format_events(self, event_array):
        events = []
        for e in event_array:
            event_string = EVENT_FORMAT.format(
                summary=e['summary'],
                creator=self.__format_person(e['organizer']),
                attendees=', '.join([self.__format_person(i)
                                    for i in e['attendees']]),
                start_date=e['start']['dateTime'],
                end_date=e['end']['dateTime'],
                link=e['htmlLink'],
                location=e.get('location', "None Set")
            )

            events.append(event_string)

        return "\n---\n".join(events)

    def execute(self, message):
        # get credentials
        service = build('calendar', 'v3',
                        credentials=self.build_google_creds())
        operation, query = self.__parse_message(message)

        if operation is None:
            return "Error accessing calendar"

        print(operation, query)

        if operation == "daterange":
            start_date, end_date = self.__parse_date_range(query)
            events_result = service.events().list(calendarId="primary", timeMin=start_date,
                                                  timeMax=end_date, singleEvents=True, orderBy='startTime').execute()
            events = events_result.get('items', [])
            return self.__format_events(events)
        elif operation == "search":
            events_result = service.events().list(
                calendarId="primary", q=query, timeMin=datetime.now(timezone.utc).isoformat()).execute()
            print(events_result)
            events = events_result.get('items', [])
            return self.__format_events(events)

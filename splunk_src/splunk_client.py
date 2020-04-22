import json
import time

import splunklib.client as client
import splunklib.results as results
from splunklib.binding import AuthenticationError

import splunk_src


class SplunkIngestion:
    def __init__(self):
        self.logger = splunk_src.get_logger()
        self._service = None
        self._connect()
        self._HOST = "localhost"
        self._PORT = 8089
        self._USERNAME = "admin"
        self._PASSWORD = "burltree136"

    def _connect(self):
        self.logger.debug('Connecting to Splunk...')
        # Create a Service instance and log in
        self._service = client.connect(
            host=splunk_src.get_setting('SPLUNK_HOST'),
            port=splunk_src.get_setting('SPLUNK_PORT'),
            username=splunk_src.get_setting('SPLUNK_USERNAME'),
            password=splunk_src.get_setting('SPLUNK_PASSWORD'))

        # Print installed apps to the console to verify login
        # for app in _service.apps:
        #     print(app.name)

        # List the saved searches that are available to the current user
        # savedsearches = self._service.saved_searches

        # for savedsearch in savedsearches:
        #     print(f'{savedsearch.name}')
        #     print(f"Query: {savedsearch['search']}")

    def execute_saved_query(self, query_name):
        if self._service is None:
            self._connect()

        # Execute a saved search and save the results
        # Retrieve the saved search
        # saved_search_name = "test_saved_query_1"
        saved_search_name = query_name
        savedSearch = self._service.saved_searches[saved_search_name]

        # Run the saved search
        job = savedSearch.dispatch()

        # Create a small delay to allow time for the update between server and client
        time.sleep(2)

        # Wait for the job to finish--poll for completion and display stats
        while True:
            job.refresh()
            stats = {"isDone": job["isDone"],
                     "doneProgress": float(job["doneProgress"])*100,
                     "scanCount": int(job["scanCount"]),
                     "eventCount": int(job["eventCount"]),
                     "resultCount": int(job["resultCount"])}
            status = ("\r%(doneProgress)03.1f%%   %(scanCount)d scanned   "
                      "%(eventCount)d matched   %(resultCount)d results") % stats

            print(status)
            if stats["isDone"] == "1":
                break
            time.sleep(2)

        event_count = int(job["eventCount"])

        if event_count == 0:
            self.logger.info("Event count is 0. Exiting")
            return

        i = 0
        events = []
        # with open(file=file_name, mode="w") as out:
        while i < event_count:
            try:
                results_stream = job.results(count=1000, offset=i)
                reader = results.ResultsReader(results_stream)
            except AuthenticationError:
                self.logger.info("Session timed our. Reauthenticating")
                self._connect()
                results_stream = job.results(count=1000, offset=i)
                reader = results.ResultsReader(results_stream)

            for result in reader:
                if isinstance(result, dict):
                    events.append(result)
                    # out.write(json.dumps(result)+'\n')
            i += 1000

        response = json.dumps(events, indent=2)
        return response

        # Save to S3 in Data Lake
        # self.save_to_s3(file_name)


if __name__ == "__main__":
    s = SplunkIngestion()
    s.logger.debug(s.search())

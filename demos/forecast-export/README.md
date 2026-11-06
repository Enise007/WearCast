# Forecast export security demo

This intentionally vulnerable, standalone demo uses synthetic weather data and
binds only to `127.0.0.1`. It does not import WearCast, load `.env` files, access
accounts, or call external services. Keep it separate from the deployed app.

## Run

From the repository root, with Python 3:

```sh
python3 demos/forecast-export/server.py
```

Open <http://127.0.0.1:8001>, enter a city, and download the CSV. No dependencies
or API keys are required. Stop with Ctrl+C.

## The finding to look for

**CSV formula injection (CWE-1236)** in `server.py`: the `city` query parameter
flows into `csv.writer` and then a downloadable spreadsheet file. CSV escaping
protects field boundaries, but does not stop spreadsheet formula interpretation.
The length check, `.strip()`, and use of the standard CSV library can make this
look like ordinary, safely escaped export code during a quick review.

For a harmless demonstration, enter `=1+1` as the city. The downloaded CSV
contains that exact value. A spreadsheet that interprets CSV formulas may show
`2` in the city cell; this depends on the application and import settings.
Viewing the CSV in a text editor will just show `=1+1`.

You can also inspect the HTTP response without opening a spreadsheet:

```sh
curl -G --data-urlencode 'city==1+1' http://127.0.0.1:8001/forecast.csv
```

Use only the arithmetic payload for this demonstration. The payload is harmless;
the underlying vulnerability would not be harmless in a production export.

## Follow-up fix for the demo

For this city field, reject formula-leading input after the existing `.strip()`
normalization, before generating the CSV:

```python
if city.startswith(("=", "+", "-", "@")):
    self.send_error(400, "Enter a city name")
    return
```

This narrow validation fits the demonstration. A general-purpose spreadsheet
export needs a strategy appropriate to its fields and target spreadsheet apps,
including handling control characters and testing formula interpretation.

## Recording notes

Add the demo files in a review PR. Show the ordinary city export first, then
show the reviewer's finding and the `=1+1` reproduction. Apply the validation
above and show that the arithmetic input returns HTTP 400 while an ordinary city
still exports. Automated detection and severity are not guaranteed; use the
actual review result in the recording.

Reference: [OWASP CSV Injection](https://owasp.org/www-community/attacks/CSV_Injection).

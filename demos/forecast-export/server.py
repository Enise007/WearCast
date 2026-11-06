"""Standalone forecast export demo using synthetic weather data."""

import argparse
import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import StringIO
from urllib.parse import parse_qs, urlsplit


INDEX = b"""<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WearCast forecast export</title>
<style>
body { font: 18px system-ui; max-width: 38rem; margin: 5rem auto; padding: 1rem; }
input, button { font: inherit; padding: .6rem; }
</style>
<h1>Export your forecast</h1>
<p>Download a sample clothing forecast for your city.</p>
<form action="/forecast.csv" method="get">
  <label for="city">City</label>
  <input id="city" name="city" value="Istanbul" maxlength="120" required>
  <button>Download CSV</button>
</form>
<p><small>Preview data only. No weather service or account connection.</small></p>
</html>
"""


def build_forecast_csv(city):
    output = StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["City", "Temperature (C)", "Conditions", "Recommendation"])
    writer.writerow([city, 18, "Partly cloudy", "Light jacket"])
    return output.getvalue().encode("utf-8")


class ForecastExportHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/":
            self.send_body(INDEX, "text/html; charset=utf-8")
            return
        if url.path != "/forecast.csv":
            self.send_error(404)
            return

        city = parse_qs(url.query).get("city", ["Istanbul"])[0].strip()
        if not city or len(city) > 120:
            self.send_error(400, "City must contain 1 to 120 characters")
            return

        self.send_body(
            build_forecast_csv(city),
            "text/csv; charset=utf-8",
            attachment="wearcast-forecast.csv",
        )

    def send_body(self, body, content_type, attachment=None):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if attachment:
            self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    with HTTPServer(("127.0.0.1", args.port), ForecastExportHandler) as server:
        print(f"Forecast export demo: http://127.0.0.1:{server.server_port}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

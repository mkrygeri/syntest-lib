# Test Results Enrichment

This module fetches synthetic test results from the Kentik API and enriches them with metadata (agent info, test config, site data) for export to InfluxDB or other time-series databases.

## Features

- Fetch test results for multiple tests over a time range
- Enrich results with agent, test, and site metadata
- Export in InfluxDB line protocol format
- Support for DNS, Ping, and HTTP test types
- Handle DNS Grid tests with multiple tasks per agent

## Usage

### Command Line

```bash
# Get last hour of results
python fetch_results.py --minutes 60

# Get last 24 hours, save to file
python fetch_results.py --hours 24 --output /tmp/results.influx

# Get specific time range
python fetch_results.py --start "2025-01-01 00:00:00" --end "2025-01-02 00:00:00"

# Filter by specific tests
python fetch_results.py --minutes 60 --tests "test-id-1,test-id-2"

# Filter by specific agents
python fetch_results.py --minutes 60 --agents "agent-id-1,agent-id-2"

# Aggregate results
python fetch_results.py --hours 24 --aggregate

# Send directly to Kentik NMS (requires KENTIK_EMAIL and KENTIK_API_TOKEN)
python fetch_results.py --minutes 60 --send-to-kentik

# Send to Kentik AND save to file
python fetch_results.py --minutes 60 --send-to-kentik --output /tmp/results.influx
```

### Python API

```python
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Initialize
client = SyntheticsClient(email="your-email@company.com", api_token="your-token")
enricher = TestResultsEnricher(client)

# Load metadata
enricher.refresh_metadata()

# Fetch results for the last hour
now = datetime.now(timezone.utc)
start_time = now - timedelta(hours=1)
end_time = now

# Get all test IDs
test_ids = list(enricher._tests_cache.keys())

# Fetch and enrich results
enriched_records = enricher.get_all_results(
    test_ids=test_ids,
    start_time=start_time,
    end_time=end_time
)

# Convert to InfluxDB line protocol
lines = enricher.to_influx_line_protocol(enriched_records)

# Write to file or send to InfluxDB
with open('results.influx', 'w') as f:
    for line in lines:
        f.write(line + '\n')
```

## InfluxDB Line Protocol Format

The output uses InfluxDB line protocol format:

```
measurement,tag1=value1,tag2=value2 field1=value1,field2=value2 timestamp
```

Example:
```
/kentik/synthetics/dns,test_id=123,test_name=DNS\ Test,agent_name=NYC-1 latency_ms=45.2,latency_health="healthy" 1609459200000000000
```

### Measurements

- `/kentik/synthetics/dns` - DNS test results
- `/kentik/synthetics/ping` - Ping test results
- `/kentik/synthetics/http` - HTTP test results

### Tags (Metadata Dimensions)

- `test_id` - Unique test identifier
- `test_name` - Human-readable test name
- `test_type` - Test type (dns, dns_grid, ping, http, etc.)
- `agent_id` - Unique agent identifier
- `agent_name` - Human-readable agent name
- `site_name` - Site where agent is located
- `health` - Overall health status

### Fields (Metric Values)

#### DNS Results
- `target` - Target domain being queried
- `server` - DNS server queried
- `latency_current` - Current DNS latency (microseconds)
- `latency_rolling_avg` - Rolling average latency (microseconds)
- `latency_rolling_stddev` - Standard deviation of latency (microseconds)
- `latency_health` - Health status of latency metric
- `response_status` - DNS response code
- `response_data` - JSON array of resolved IP addresses

#### Ping Results
- `target` - Target host being pinged
- `dst_ip` - Destination IP address
- `latency_current` - Current round-trip time (microseconds)
- `latency_rolling_avg` - Rolling average RTT (microseconds)
- `latency_rolling_stddev` - Standard deviation of RTT (microseconds)
- `latency_health` - Health status of latency metric
- `packet_loss_current` - Current packet loss percentage
- `packet_loss_health` - Health status of packet loss
- `jitter_current` - Current jitter (microseconds)
- `jitter_rolling_avg` - Rolling average jitter (microseconds)
- `jitter_rolling_stddev` - Standard deviation of jitter (microseconds)
- `jitter_health` - Health status of jitter metric

#### HTTP Results
- `target` - Target URL being tested
- `dst_ip` - Destination IP address
- `latency_current` - Current page load time (microseconds)
- `latency_rolling_avg` - Rolling average page load time (microseconds)
- `latency_rolling_stddev` - Standard deviation of page load time (microseconds)
- `latency_health` - Health status of latency metric
- `http_status` - HTTP status code (200, 404, 500, etc.)
- `response_size` - Response size in bytes
- `response_data` - JSON with detailed browser timing metrics

**Note:** All latency values are in **microseconds** for maximum precision. To convert to milliseconds: divide by 1,000. To convert to seconds: divide by 1,000,000.

For detailed information about all available metrics and how to use them, see [METRICS_REFERENCE.md](METRICS_REFERENCE.md).

## Sending to Kentik NMS

### Direct Send (Recommended)

The easiest way to send metrics to Kentik NMS is using the `--send-to-kentik` flag:

```bash
# Send last hour of metrics directly to Kentik NMS
python fetch_results.py --minutes 60 --send-to-kentik

# Send and also save to file for backup
python fetch_results.py --minutes 60 --send-to-kentik --output /tmp/backup.influx
```

The script uses the same `KENTIK_EMAIL` and `KENTIK_API_TOKEN` environment variables for authentication.

### Python API

```python
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Initialize and fetch results
client = SyntheticsClient(email="your-email@company.com", api_token="your-token")
enricher = TestResultsEnricher(client)
enricher.refresh_metadata()

# Get results and convert to line protocol
enriched_records = enricher.get_all_results(
    test_ids=test_ids,
    start_time=start_time,
    end_time=end_time
)
lines = enricher.to_influx_line_protocol(enriched_records)

# Send directly to Kentik NMS
enricher.send_to_kentik(
    lines=lines,
    email="your-email@company.com",
    api_token="your-token"
)
```

## Importing to InfluxDB

### Using the influx CLI

```bash
# Import line protocol file
influx write \
  --bucket your-bucket \
  --org your-org \
  --precision ns \
  --file results.influx
```

### Using the HTTP API

```bash
# Import via HTTP
curl -X POST "http://localhost:8086/api/v2/write?org=your-org&bucket=your-bucket&precision=ns" \
  --header "Authorization: Token your-token" \
  --data-binary @results.influx
```

### Using Python

```python
from influxdb_client import InfluxDBClient

client = InfluxDBClient(url="http://localhost:8086", token="your-token", org="your-org")
write_api = client.write_api()

with open('results.influx', 'r') as f:
    write_api.write(bucket="your-bucket", record=f.read())
```

## Scheduling

### Sending to Kentik NMS on a Schedule

To continuously monitor your synthetic tests, schedule the script to run regularly:

#### Using cron (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add this line to run every 5 minutes (matching typical test frequency)
*/5 * * * * cd /path/to/syntest-lib && /path/to/venv/bin/python fetch_results.py --minutes 5 --send-to-kentik >> /var/log/kentik-metrics.log 2>&1

# Or with explicit environment variables
*/5 * * * * export KENTIK_EMAIL="your@email.com" KENTIK_API_TOKEN="token" && cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --send-to-kentik
```

#### Using systemd timer (Linux)

Create `/etc/systemd/system/kentik-metrics.service`:

```ini
[Unit]
Description=Send Kentik synthetic test metrics to NMS

[Service]
Type=oneshot
Environment=KENTIK_EMAIL=your-email@company.com
Environment=KENTIK_API_TOKEN=your-token
WorkingDirectory=/path/to/syntest-lib
ExecStart=/path/to/venv/bin/python fetch_results.py --minutes 5 --send-to-kentik
```

Create `/etc/systemd/system/kentik-metrics.timer`:

```ini
[Unit]
Description=Send Kentik metrics every 5 minutes

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
systemctl enable kentik-metrics.timer
systemctl start kentik-metrics.timer
systemctl status kentik-metrics.timer
```

### Saving to File on a Schedule

For InfluxDB import or backup purposes:

### Using cron

```bash
# Fetch results every hour
0 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 60 --output /var/log/kentik/results.influx

# Import to InfluxDB every hour
5 * * * * influx write --bucket syntest --file /var/log/kentik/results.influx
```

### Using systemd timer

Create `/etc/systemd/system/kentik-results.service`:

```ini
[Unit]
Description=Fetch Kentik synthetic test results

[Service]
Type=oneshot
Environment=KENTIK_EMAIL=your-email@company.com
Environment=KENTIK_API_TOKEN=your-token
ExecStart=/usr/bin/python3 /path/to/syntest-lib/fetch_results.py --minutes 60 --output /tmp/kentik-results.influx
ExecStartPost=/usr/bin/influx write --bucket syntest --file /tmp/kentik-results.influx
```

Create `/etc/systemd/system/kentik-results.timer`:

```ini
[Unit]
Description=Fetch Kentik results every hour

[Timer]
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and start:

```bash
systemctl enable kentik-results.timer
systemctl start kentik-results.timer
```

## Environment Variables

The tool requires these environment variables:

- `KENTIK_EMAIL` - Your Kentik account email
- `KENTIK_API_TOKEN` - Your Kentik API token

Example:

```bash
export KENTIK_EMAIL=your-email@company.com
export KENTIK_API_TOKEN=your-api-token
```

## Error Handling

The enricher handles missing metadata gracefully:

- If agent metadata is not found, fields will be `None`
- If test metadata is not found, fields will be `None`
- If results have no data, they are skipped
- API errors are logged and can be retried

## Performance Considerations

- **Batch Size**: Fetching results for many tests at once is efficient
- **Time Range**: Larger time ranges return more data but take longer
- **Caching**: Metadata is cached to avoid repeated API calls
- **Rate Limiting**: The client includes automatic rate limiting

## Troubleshooting

### No results returned

- Check that tests exist and have run during the time range
- Verify test IDs are correct
- Ensure agents are active and reporting

### Missing metadata

- Call `enricher.refresh_metadata()` before fetching results
- Check that agents/tests exist in the Kentik API

### InfluxDB import errors

- Verify line protocol format with `head results.influx`
- Check timestamp is in nanoseconds (19 digits)
- Ensure field values are properly typed (numbers vs strings)

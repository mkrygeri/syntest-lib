# Kentik NMS Integration - Quick Start

This guide shows you how to send synthetic test results directly to Kentik NMS.

## Overview

The integration fetches test results from the Kentik Synthetics API, enriches them with metadata (agent names, test names, site info), and sends them to Kentik NMS in InfluxDB line protocol format.

## Prerequisites

- Python 3.7+
- Kentik account with API access
- Environment variables set:
  ```bash
  export KENTIK_EMAIL="your-email@company.com"
  export KENTIK_API_TOKEN="your-api-token"
  ```

## Quick Start

### 1. Send Metrics Once (Manual)

```bash
# Send last 5 minutes of results
python fetch_results.py --minutes 5 --send-to-kentik

# Send last hour
python fetch_results.py --minutes 60 --send-to-kentik

# Send and also save backup to file
python fetch_results.py --minutes 5 --send-to-kentik --output /tmp/backup.influx
```

### 2. Schedule Automatic Sending (Recommended)

#### Option A: Cron (simplest)

```bash
# Edit crontab
crontab -e

# Add this line (runs every 5 minutes)
*/5 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --send-to-kentik
```

#### Option B: Systemd Timer (Linux)

See [docs/results_enrichment.md](docs/results_enrichment.md) for full systemd setup.

### 3. Verify in Kentik NMS UI

1. Open https://portal.kentik.com/
2. Navigate to NMS section
3. Create a query with these measurements:
   - `/kentik/synthetics/dns` - DNS test metrics
   - `/kentik/synthetics/ping` - Ping test metrics  
   - `/kentik/synthetics/http` - HTTP test metrics

## Available Metrics

### DNS Tests (`/kentik/synthetics/dns`)
- `latency_current` - Current DNS query latency (microseconds)
- `latency_rolling_avg` - Rolling average latency (microseconds)
- `latency_rolling_stddev` - Standard deviation of latency (microseconds)
- `latency_health` - Health status of latency metric
- `response_status` - DNS response status code
- `response_data` - JSON array of resolved IP addresses
- `target` - Target domain being queried
- `server` - DNS server queried

Tags: `test_id`, `test_name`, `test_type`, `agent_id`, `agent_name`, `site_name`, `health`

### Ping Tests (`/kentik/synthetics/ping`)
- `latency_current` - Current round-trip time (microseconds)
- `latency_rolling_avg` - Rolling average RTT (microseconds)
- `latency_rolling_stddev` - Standard deviation of RTT (microseconds)
- `latency_health` - Health status of latency metric
- `packet_loss_current` - Current packet loss percentage (0-100)
- `packet_loss_health` - Health status of packet loss metric
- `jitter_current` - Current jitter (microseconds)
- `jitter_rolling_avg` - Rolling average jitter (microseconds)
- `jitter_rolling_stddev` - Standard deviation of jitter (microseconds)
- `jitter_health` - Health status of jitter metric
- `target` - Target host being pinged
- `dst_ip` - Destination IP address

Tags: `test_id`, `test_name`, `test_type`, `agent_id`, `agent_name`, `site_name`, `health`

### HTTP Tests (`/kentik/synthetics/http`)
- `latency_current` - Current page load time (microseconds)
- `latency_rolling_avg` - Rolling average page load time (microseconds)
- `latency_rolling_stddev` - Standard deviation of page load time (microseconds)
- `latency_health` - Health status of latency metric
- `http_status` - HTTP status code (200, 404, 500, etc.)
- `response_size` - Response size in bytes
- `response_data` - JSON with detailed browser timing metrics
- `target` - Target URL being tested
- `dst_ip` - Destination IP address

Tags: `test_id`, `test_name`, `test_type`, `agent_id`, `agent_name`, `site_name`, `health`

**Note:** All latency values are in **microseconds**. To convert:
- Milliseconds: divide by 1,000
- Seconds: divide by 1,000,000

For a complete reference with query examples, see [docs/METRICS_REFERENCE.md](docs/METRICS_REFERENCE.md).

## Python API Usage

```python
from datetime import datetime, timedelta, timezone
from syntest_lib import SyntheticsClient
from syntest_lib.results_enricher import TestResultsEnricher

# Initialize
client = SyntheticsClient(email="your@email.com", api_token="your-token")
enricher = TestResultsEnricher(client)

# Load metadata
enricher.refresh_metadata()

# Fetch results
now = datetime.now(timezone.utc)
test_ids = list(enricher._tests_cache.keys())

enriched_records = enricher.get_all_results(
    test_ids=test_ids,
    start_time=now - timedelta(minutes=5),
    end_time=now
)

# Convert to line protocol
lines = enricher.to_influx_line_protocol(enriched_records)

# Send to Kentik NMS
enricher.send_to_kentik(
    lines=lines,
    email="your@email.com",
    api_token="your-token"
)
```

## Troubleshooting

### No data appearing in Kentik NMS

1. **Check credentials**: Verify `KENTIK_EMAIL` and `KENTIK_API_TOKEN` are set correctly
2. **Check tests are running**: Ensure your synthetic tests are active and producing results
3. **Check time range**: Try `--minutes 60` instead of `--minutes 5` to get more data
4. **Check logs**: Run with `--verbose` flag to see detailed logging

### Authentication errors

```bash
# Verify your credentials work
python -c "from syntest_lib import SyntheticsClient; c = SyntheticsClient(email='your@email.com', api_token='your-token'); print(len(c.list_tests().tests), 'tests found')"
```

### Rate limiting

The client includes automatic rate limiting. If you hit rate limits:
- Increase time between runs (e.g., every 10 minutes instead of 5)
- Reduce number of tests queried using `--tests` filter

## Best Practices

1. **Match test frequency**: If tests run every 5 minutes, collect results every 5 minutes
2. **Use filtering**: For large deployments, consider filtering by test or agent to reduce load
3. **Monitor the monitor**: Set up alerting if metrics stop flowing to Kentik NMS
4. **Keep backups**: Use `--output` to save line protocol files as backup
5. **Start small**: Test with a few tests first, then scale up

## Example Cron Configurations

```bash
# Every 5 minutes (typical)
*/5 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --send-to-kentik

# Every 10 minutes with backup
*/10 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 10 --send-to-kentik --output /var/log/kentik/backup-$(date +\%Y\%m\%d-\%H\%M).influx

# Hourly summary
0 * * * * cd /path/to/syntest-lib && python fetch_results.py --hours 1 --send-to-kentik --aggregate

# Specific tests only
*/5 * * * * cd /path/to/syntest-lib && python fetch_results.py --minutes 5 --tests "test1,test2,test3" --send-to-kentik
```

## Support

- Documentation: [docs/results_enrichment.md](docs/results_enrichment.md)
- Example: [examples/send_to_kentik_example.py](examples/send_to_kentik_example.py)
- GitHub: https://github.com/mkrygeri/syntest-lib

## Technical Details

- **Endpoint**: `https://grpc.api.kentik.com/kmetrics/v202207/metrics/api/v2/write`
- **Format**: InfluxDB Line Protocol with nanosecond precision
- **Authentication**: Same Kentik API credentials used for Synthetics API
- **Measurements**: Path-like structure (`/kentik/synthetics/dns`)
- **Rate Limiting**: Automatic with exponential backoff

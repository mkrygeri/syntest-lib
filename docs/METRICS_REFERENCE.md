# Kentik Synthetics Metrics Reference

This document provides a complete reference of all metrics available from the Kentik Synthetics API and how they are represented in InfluxDB line protocol format for Kentik NMS.

## Table of Contents

- [Measurement Names](#measurement-names)
- [Common Tags](#common-tags)
- [DNS Metrics](#dns-metrics)
- [HTTP Metrics](#http-metrics)
- [Ping Metrics](#ping-metrics)
- [Understanding Rolling Statistics](#understanding-rolling-statistics)
- [Health Status Values](#health-status-values)

## Measurement Names

All metrics use path-like measurement names for clear organization in Kentik NMS:

- `/kentik/synthetics/dns` - DNS resolution tests
- `/kentik/synthetics/http` - HTTP/HTTPS page load tests
- `/kentik/synthetics/ping` - ICMP ping tests

## Common Tags

Every metric includes these tags for filtering and grouping:

| Tag | Type | Description | Example |
|-----|------|-------------|---------|
| `test_id` | string | Unique test identifier | `188929` |
| `test_name` | string | Human-readable test name | `kentik` |
| `test_type` | string | Type of synthetic test | `page_load`, `dns`, `ip` |
| `agent_id` | string | Unique agent identifier | `69959` |
| `agent_name` | string | Human-readable agent name | `kubernetes-master` |
| `site_name` | string | Site/location name | `NH - Datacenter` |
| `health` | string | Overall health status | `healthy`, `warning`, `critical` |

## Test Configuration Tags

These tags provide context about what is being tested and how:

| Tag | Test Types | Description | Example |
|-----|------------|-------------|---------|
| `test_target` | All | Primary target (URL, hostname, IP) | `google.com`, `https://www.kentik.com` |
| `test_dns_server` | DNS, DNS Grid | DNS server being queried | `8.8.8.8`, `1.1.1.1` |
| `test_dns_record_type` | DNS, DNS Grid | Type of DNS record | `A`, `AAAA`, `MX`, `CNAME` |
| `test_http_method` | URL, Page Load | HTTP request method | `GET`, `POST`, `PUT` |
| `test_port` | DNS, DNS Grid | Target port number | `53`, `8053` |
| `test_period` | All | Test frequency in seconds | `60`, `300` |
| `test_labels` | All | Comma-separated test labels | `production,critical` |

**Note:** These tags enable powerful filtering and grouping. See [ENHANCED_TAGS_GUIDE.md](ENHANCED_TAGS_GUIDE.md) for detailed query examples.

## DNS Metrics

**Measurement:** `/kentik/synthetics/dns`

### Fields

| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `target` | string | - | DNS query target (domain name) |
| `server` | string | - | DNS server queried |
| `latency_current` | float | microseconds | Current DNS resolution latency |
| `latency_rolling_avg` | float | microseconds | Rolling average of DNS latency |
| `latency_rolling_stddev` | float | microseconds | Standard deviation of DNS latency |
| `latency_health` | string | - | Health status of latency metric |
| `response_status` | integer | - | DNS response code (0=success) |
| `response_data` | string | - | JSON array of resolved IP addresses |

### Example Line Protocol

```
/kentik/synthetics/dns,test_id=279947,test_name=Simple\ DNS\ Test,test_type=dns,agent_id=649,agent_name=Mumbai\ India,site_name=Akamai\ (Linode)\ SG\ (63949),health=healthy target="",server="",latency_current=3576,latency_rolling_avg=9738,latency_rolling_stddev=20193,latency_health="healthy",response_status=0,response_data="[\"142.251.42.78\"]" 1759873020000000000
```

### Query Examples

```sql
-- Average DNS latency by test
SELECT MEAN(latency_current) FROM /kentik/synthetics/dns GROUP BY test_name

-- DNS latency with rolling statistics
SELECT latency_current, latency_rolling_avg, latency_rolling_stddev 
FROM /kentik/synthetics/dns 
WHERE test_name = 'google-dns'

-- DNS health issues
SELECT * FROM /kentik/synthetics/dns WHERE latency_health != 'healthy'
```

## HTTP Metrics

**Measurement:** `/kentik/synthetics/http`

### Fields

| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `target` | string | - | URL or endpoint being tested |
| `dst_ip` | string | - | Destination IP address |
| `latency_current` | float | microseconds | Current page load time |
| `latency_rolling_avg` | float | microseconds | Rolling average of page load time |
| `latency_rolling_stddev` | float | microseconds | Standard deviation of page load time |
| `latency_health` | string | - | Health status of latency metric |
| `http_status` | integer | - | HTTP response code (200, 404, 500, etc.) |
| `response_size` | integer | bytes | Size of HTTP response |
| `response_data` | string | - | JSON with detailed timing metrics |

### Response Data Details

The `response_data` field contains a JSON array with detailed browser timing metrics:

- `connectEnd` / `connectStart` - TCP connection timing
- `domComplete` - DOM processing complete time
- `domContentLoadedEventEnd` - DOM content loaded time
- `domInteractive` - DOM interactive time
- `domainLookupEnd` / `domainLookupStart` - DNS lookup timing
- `duration` - Total page load duration
- `fetchStart` - Resource fetch start time
- `https_expiry_timestamp` - SSL certificate expiry (Unix timestamp)
- `loadEventEnd` / `loadEventStart` - Page load event timing
- `requestStart` - HTTP request start time
- `responseEnd` / `responseStart` - HTTP response timing
- `secureConnectionStart` - TLS handshake start time
- `statusCode` - HTTP status code
- `tlsProtocol` - TLS version used

### Example Line Protocol

```
/kentik/synthetics/http,test_id=188929,test_name=kentik,test_type=page_load,agent_id=69959,agent_name=kubernetes-master,site_name=NH\ -\ Datacenter,health=critical target="",dst_ip="18.208.88.157",latency_current=2880300,latency_rolling_avg=2699550,latency_rolling_stddev=637107,latency_health="healthy",http_status=200,response_size=663628,response_data="[{\"duration\":2880300,\"domComplete\":2869500,...}]" 1759873020000000000
```

### Query Examples

```sql
-- Average page load time by test
SELECT MEAN(latency_current) FROM /kentik/synthetics/http GROUP BY test_name

-- Page load performance with variance
SELECT latency_current, latency_rolling_avg, latency_rolling_stddev 
FROM /kentik/synthetics/http 
WHERE test_name = 'kentik'

-- HTTP errors
SELECT * FROM /kentik/synthetics/http WHERE http_status >= 400

-- Large responses
SELECT * FROM /kentik/synthetics/http WHERE response_size > 1000000
```

## Ping Metrics

**Measurement:** `/kentik/synthetics/ping`

### Fields

| Field Name | Type | Unit | Description |
|------------|------|------|-------------|
| `target` | string | - | Target host or IP being pinged |
| `dst_ip` | string | - | Destination IP address |
| `latency_current` | float | microseconds | Current round-trip time |
| `latency_rolling_avg` | float | microseconds | Rolling average of RTT |
| `latency_rolling_stddev` | float | microseconds | Standard deviation of RTT |
| `latency_health` | string | - | Health status of latency metric |
| `packet_loss_current` | float | percentage | Current packet loss percentage |
| `packet_loss_health` | string | - | Health status of packet loss |
| `jitter_current` | float | microseconds | Current jitter (latency variation) |
| `jitter_rolling_avg` | float | microseconds | Rolling average of jitter |
| `jitter_rolling_stddev` | float | microseconds | Standard deviation of jitter |
| `jitter_health` | string | - | Health status of jitter metric |

### Example Line Protocol

```
/kentik/synthetics/ping,test_id=219739,test_name=FRC-MAE-RADIUS_AUTH_Monitoring,test_type=ip,agent_id=56183,agent_name=Washington\ DC\,\ United\ States,site_name=Lumen\ (Level3)\,US\ (3356),health=healthy target="",dst_ip="196.20.188.10",latency_current=233815,latency_rolling_avg=235145,latency_rolling_stddev=2225,latency_health="healthy",packet_loss_current=0.0,packet_loss_health="healthy",jitter_current=229,jitter_rolling_avg=3165,jitter_rolling_stddev=4194,jitter_health="healthy" 1759873020000000000
```

### Query Examples

```sql
-- Average ping latency by location
SELECT MEAN(latency_current) FROM /kentik/synthetics/ping GROUP BY site_name

-- Latency with rolling statistics
SELECT latency_current, latency_rolling_avg, latency_rolling_stddev 
FROM /kentik/synthetics/ping 
WHERE test_name = 'radius-monitoring'

-- Packet loss issues
SELECT * FROM /kentik/synthetics/ping WHERE packet_loss_current > 0

-- High jitter connections
SELECT * FROM /kentik/synthetics/ping WHERE jitter_current > 10000

-- Network performance summary
SELECT 
  MEAN(latency_current) as avg_latency,
  MEAN(jitter_current) as avg_jitter,
  MAX(packet_loss_current) as max_packet_loss
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_name
```

## Understanding Rolling Statistics

Rolling statistics provide context for understanding if current values are normal or anomalous:

### Rolling Average (`*_rolling_avg`)

The rolling average represents the typical value over recent measurements (typically last 10-20 samples). Compare current values against this baseline:

- If `latency_current` >> `latency_rolling_avg`: Current latency is unusually high
- If `latency_current` << `latency_rolling_avg`: Current latency is unusually low (good!)
- If `latency_current` ≈ `latency_rolling_avg`: Current latency is typical

### Rolling Standard Deviation (`*_rolling_stddev`)

Standard deviation measures variability/stability:

- **Low stddev** (< 10% of avg): Very stable connection
- **Medium stddev** (10-30% of avg): Normal variability
- **High stddev** (> 30% of avg): Unstable/inconsistent connection

### Anomaly Detection Example

```python
# Calculate if current latency is anomalous
deviation_from_avg = abs(latency_current - latency_rolling_avg)
num_stddevs = deviation_from_avg / latency_rolling_stddev

if num_stddevs > 3:
    print("⚠️  Anomaly detected! Latency is 3+ standard deviations from normal")
elif num_stddevs > 2:
    print("⚡ Elevated latency (2+ stddevs from normal)")
else:
    print("✅ Latency within normal range")
```

## Health Status Values

The `health` and `*_health` fields can have these values:

| Value | Meaning | Action |
|-------|---------|--------|
| `healthy` | Metric within normal thresholds | No action needed |
| `warning` | Metric approaching threshold | Monitor closely |
| `critical` | Metric exceeded threshold | Investigate immediately |

### Health Checks in Queries

```sql
-- Count issues by severity
SELECT COUNT(*) FROM /kentik/synthetics/ping 
WHERE time > now() - 1h 
GROUP BY health

-- Tests with latency issues
SELECT * FROM /kentik/synthetics/ping 
WHERE latency_health != 'healthy'

-- Critical packet loss
SELECT * FROM /kentik/synthetics/ping 
WHERE packet_loss_health = 'critical'
```

## Data Retention and Precision

- **Timestamp precision:** Nanoseconds (1759873020000000000 = 2025-10-07 21:17:00 UTC)
- **Latency units:** Microseconds (1 second = 1,000,000 microseconds)
- **Packet loss units:** Percentage (0.0 to 100.0)
- **Data retention:** Determined by your Kentik NMS configuration

## Converting Microseconds to Milliseconds

Many monitoring tools display latency in milliseconds. To convert:

```sql
-- DNS latency in milliseconds
SELECT latency_current / 1000 AS latency_ms 
FROM /kentik/synthetics/dns

-- HTTP page load time in seconds
SELECT latency_current / 1000000 AS latency_seconds 
FROM /kentik/synthetics/http
```

## Best Practices

1. **Use rolling statistics** for alerting rather than single current values to reduce false positives
2. **Monitor stddev** to detect intermittent issues even when averages look normal
3. **Correlate metrics** across DNS, Ping, and HTTP to pinpoint issues:
   - High DNS latency but normal ping → DNS server issues
   - High ping latency → Network path issues
   - High HTTP latency but normal ping → Application/server issues
4. **Group by location** (`site_name`) to identify geographic patterns
5. **Track health status changes** over time to understand trend patterns

## Example Dashboard Queries

### Network Health Overview
```sql
SELECT 
  COUNT(*) as total_tests,
  COUNT(CASE WHEN health = 'healthy' THEN 1 END) as healthy,
  COUNT(CASE WHEN health = 'warning' THEN 1 END) as warning,
  COUNT(CASE WHEN health = 'critical' THEN 1 END) as critical
FROM /kentik/synthetics/ping
WHERE time > now() - 5m
```

### Latency Trends with Anomalies
```sql
SELECT 
  test_name,
  latency_current,
  latency_rolling_avg,
  (latency_current - latency_rolling_avg) / latency_rolling_stddev as stddev_from_avg
FROM /kentik/synthetics/ping
WHERE time > now() - 1h
ORDER BY stddev_from_avg DESC
```

### Top 10 Slowest Tests
```sql
SELECT 
  test_name, 
  agent_name,
  latency_current / 1000 as latency_ms
FROM /kentik/synthetics/http
WHERE time > now() - 5m
ORDER BY latency_current DESC
LIMIT 10
```

# Enhanced Tags Guide - Powerful Query Capabilities

This document explains the enhanced tag system that allows you to filter and group metrics by test configuration details.

## Overview

Tags in InfluxDB are indexed metadata that you can use for filtering and grouping. The enhanced tag system extracts test configuration details and adds them as tags, enabling powerful queries.

## Complete Tag Reference

### Base Tags (All Test Types)

| Tag | Description | Example | Usage |
|-----|-------------|---------|-------|
| `test_id` | Unique test identifier | `188929` | Filter specific test |
| `test_name` | Human-readable test name | `kentik` | Group by test name |
| `test_type` | Type of test | `page_load`, `dns`, `ip` | Filter by test type |
| `agent_id` | Unique agent identifier | `69959` | Filter specific agent |
| `agent_name` | Agent display name | `kubernetes-master` | Group by agent |
| `site_name` | Site/location name | `NH - Datacenter` | Group by location |
| `health` | Overall health status | `healthy`, `critical` | Filter unhealthy tests |

### Test Configuration Tags

| Tag | Test Types | Description | Example |
|-----|------------|-------------|---------|
| `test_target` | All | Primary target (URL, IP, hostname) | `https://www.kentik.com`, `8.8.8.8`, `google.com` |
| `test_dns_server` | DNS, DNS Grid | DNS server being queried | `8.8.8.8`, `1.1.1.1` |
| `test_dns_record_type` | DNS, DNS Grid | DNS record type | `A`, `AAAA`, `MX`, `CNAME` |
| `test_http_method` | URL, Page Load | HTTP method | `GET`, `POST`, `PUT` |
| `test_port` | DNS, DNS Grid | Target port number | `53`, `8053` |
| `test_period` | All | Test frequency (seconds) | `60`, `300` |
| `test_labels` | All | Comma-separated labels | `production,critical` |

## Query Examples

### 1. Filter by Target

```sql
-- All tests targeting a specific domain
SELECT * FROM /kentik/synthetics/dns 
WHERE test_target = 'google.com'

-- All tests targeting Kentik's website
SELECT * FROM /kentik/synthetics/http 
WHERE test_target = 'https://www.kentik.com'

-- Group latency by target
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
GROUP BY test_target
```

### 2. DNS Server Analysis

```sql
-- Compare performance across DNS servers
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
GROUP BY test_dns_server

-- Find issues with specific DNS server
SELECT * FROM /kentik/synthetics/dns 
WHERE test_dns_server = '8.8.8.8' 
  AND latency_health != 'healthy'

-- DNS server performance by record type
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
GROUP BY test_dns_server, test_dns_record_type
```

### 3. DNS Record Type Analysis

```sql
-- Compare A vs AAAA query performance
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
WHERE test_dns_record_type IN ('A', 'AAAA')
GROUP BY test_dns_record_type

-- MX record query issues
SELECT * FROM /kentik/synthetics/dns 
WHERE test_dns_record_type = 'MX' 
  AND (latency_current > 50000 OR response_status != 0)
```

### 4. HTTP Method Analysis

```sql
-- Compare GET vs POST performance
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/http 
GROUP BY test_http_method

-- POST request failures
SELECT * FROM /kentik/synthetics/http 
WHERE test_http_method = 'POST' 
  AND http_status >= 400
```

### 5. Test Frequency Analysis

```sql
-- Performance by test period
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/ping 
GROUP BY test_period

-- High-frequency tests (every minute)
SELECT * FROM /kentik/synthetics/ping 
WHERE test_period = 60
```

### 6. Label-Based Queries

```sql
-- Critical infrastructure tests
SELECT * FROM /kentik/synthetics/http 
WHERE test_labels =~ /critical/

-- Production environment issues
SELECT * FROM /kentik/synthetics/ping 
WHERE test_labels =~ /production/ 
  AND health != 'healthy'

-- Count tests by label category
SELECT COUNT(*) 
FROM /kentik/synthetics/dns 
WHERE test_labels != '' 
GROUP BY test_labels
```

### 7. Multi-Dimension Analysis

```sql
-- DNS performance by server, record type, and target
SELECT 
  test_dns_server,
  test_dns_record_type,
  test_target,
  MEAN(latency_current) as avg_latency,
  MAX(latency_current) as max_latency
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY test_dns_server, test_dns_record_type, test_target

-- HTTP performance by target and method
SELECT 
  test_target,
  test_http_method,
  MEAN(latency_current) as avg_latency,
  P95(latency_current) as p95_latency
FROM /kentik/synthetics/http 
WHERE time > now() - 1h
GROUP BY test_target, test_http_method

-- Location-based DNS server performance
SELECT 
  site_name,
  test_dns_server,
  MEAN(latency_current) as avg_latency
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY site_name, test_dns_server
```

### 8. Comparative Queries

```sql
-- Compare same target across different agents
SELECT 
  agent_name,
  MEAN(latency_current) as avg_latency
FROM /kentik/synthetics/ping 
WHERE test_target = '8.8.8.8' 
  AND time > now() - 1h
GROUP BY agent_name
ORDER BY avg_latency DESC

-- Compare different DNS servers for same query
SELECT 
  test_dns_server,
  MEAN(latency_current) as avg_latency,
  COUNT(*) as query_count
FROM /kentik/synthetics/dns 
WHERE test_target = 'google.com' 
  AND test_dns_record_type = 'A'
  AND time > now() - 1h
GROUP BY test_dns_server

-- Compare test frequencies
SELECT 
  test_period,
  MEAN(latency_current) as avg_latency,
  MAX(latency_rolling_stddev) as max_variability
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_period
```

## Dashboard Examples

### DNS Server Health Dashboard

```sql
-- Panel 1: DNS Server Latency
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY test_dns_server

-- Panel 2: Query Success Rate by Server
SELECT 
  COUNT(CASE WHEN response_status = 0 THEN 1 END) / COUNT(*) * 100 as success_rate
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY test_dns_server

-- Panel 3: Record Type Distribution
SELECT COUNT(*) 
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY test_dns_record_type

-- Panel 4: Top 10 Slowest Targets
SELECT 
  test_target,
  test_dns_server,
  MEAN(latency_current) as avg_latency
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY test_target, test_dns_server
ORDER BY avg_latency DESC
LIMIT 10
```

### HTTP Performance by Target Dashboard

```sql
-- Panel 1: Response Time by Target
SELECT 
  test_target,
  MEAN(latency_current) / 1000000 as latency_seconds
FROM /kentik/synthetics/http 
WHERE time > now() - 1h
GROUP BY test_target

-- Panel 2: HTTP Status Codes
SELECT COUNT(*) 
FROM /kentik/synthetics/http 
WHERE time > now() - 1h
GROUP BY http_status

-- Panel 3: Error Rate by Target
SELECT 
  test_target,
  COUNT(CASE WHEN http_status >= 400 THEN 1 END) / COUNT(*) * 100 as error_rate
FROM /kentik/synthetics/http 
WHERE time > now() - 1h
GROUP BY test_target

-- Panel 4: Method Performance
SELECT 
  test_http_method,
  MEAN(latency_current) / 1000 as latency_ms
FROM /kentik/synthetics/http 
WHERE time > now() - 1h
GROUP BY test_http_method
```

### Target Comparison Dashboard

```sql
-- Panel 1: Latency Distribution by Target
SELECT 
  test_target,
  MEAN(latency_current) as avg,
  P50(latency_current) as median,
  P95(latency_current) as p95,
  P99(latency_current) as p99
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_target

-- Panel 2: Geographic Performance
SELECT 
  test_target,
  site_name,
  MEAN(latency_current) / 1000 as latency_ms
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_target, site_name

-- Panel 3: Target Health Status
SELECT COUNT(*) 
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_target, health

-- Panel 4: Packet Loss by Target
SELECT 
  test_target,
  MEAN(packet_loss_current) as avg_packet_loss
FROM /kentik/synthetics/ping 
WHERE time > now() - 1h
GROUP BY test_target
HAVING avg_packet_loss > 0
```

## Best Practices

### 1. **Use Specific Tags for Filtering**

✅ **Good:**
```sql
SELECT * FROM /kentik/synthetics/dns 
WHERE test_dns_server = '8.8.8.8' 
  AND test_dns_record_type = 'A'
```

❌ **Avoid:**
```sql
SELECT * FROM /kentik/synthetics/dns 
WHERE server =~ /8.8.8.8/  -- Server is a field, not a tag
```

### 2. **Group by Multiple Dimensions**

```sql
-- Understand performance patterns across multiple dimensions
SELECT 
  site_name,
  test_target,
  test_dns_server,
  MEAN(latency_current) as avg_latency
FROM /kentik/synthetics/dns 
WHERE time > now() - 1h
GROUP BY site_name, test_target, test_dns_server
```

### 3. **Use Labels for Categorization**

```sql
-- Filter by infrastructure tier
SELECT * FROM /kentik/synthetics/ping 
WHERE test_labels =~ /tier-1/

-- Combine with other filters
SELECT * FROM /kentik/synthetics/http 
WHERE test_labels =~ /production/ 
  AND site_name = 'US-East'
  AND latency_health != 'healthy'
```

### 4. **Leverage Test Configuration for Troubleshooting**

```sql
-- Find which DNS servers have issues with specific record types
SELECT 
  test_dns_server,
  test_dns_record_type,
  COUNT(*) as issue_count,
  AVG(latency_current) as avg_latency
FROM /kentik/synthetics/dns 
WHERE latency_health != 'healthy'
  AND time > now() - 1h
GROUP BY test_dns_server, test_dns_record_type

-- Identify targets with consistently high latency
SELECT 
  test_target,
  agent_name,
  COUNT(*) as high_latency_count
FROM /kentik/synthetics/ping 
WHERE latency_current > latency_rolling_avg * 2
  AND time > now() - 1h
GROUP BY test_target, agent_name
HAVING high_latency_count > 10
```

## Alerting Examples

### DNS Server Issues

```sql
ALERT: DNS Server Slow Response
SELECT MEAN(latency_current) 
FROM /kentik/synthetics/dns 
WHERE time > now() - 5m
GROUP BY test_dns_server
HAVING MEAN(latency_current) > 50000  -- 50ms
```

### Target Unavailability

```sql
ALERT: HTTP Target Returning Errors
SELECT COUNT(*) 
FROM /kentik/synthetics/http 
WHERE test_target = 'https://www.example.com'
  AND http_status >= 400
  AND time > now() - 5m
HAVING COUNT(*) > 3
```

### Critical Infrastructure

```sql
ALERT: Critical Service Degraded
SELECT COUNT(*) 
FROM /kentik/synthetics/ping 
WHERE test_labels =~ /critical/
  AND (packet_loss_current > 0 OR latency_health != 'healthy')
  AND time > now() - 5m
HAVING COUNT(*) > 0
```

## Tag Cardinality Considerations

Be mindful of tag cardinality (number of unique values):

- **Low Cardinality** (Good for tags):
  - `test_dns_record_type` - ~10 values (A, AAAA, MX, etc.)
  - `test_http_method` - ~7 values (GET, POST, PUT, etc.)
  - `test_dns_server` - Usually < 100 values
  - `health` - 3 values (healthy, warning, critical)

- **Medium Cardinality** (Still good):
  - `test_target` - Could be 100s-1000s of unique targets
  - `agent_name` - Usually < 500 agents
  - `site_name` - Usually < 100 sites

- **High Cardinality** (Use carefully):
  - `test_labels` - Could have many unique combinations
  - Consider using regular expressions to match label patterns

## Migration from Fields to Tags

If you were previously querying fields like `target` or `server`, update your queries:

**Old Way (Fields):**
```sql
SELECT * FROM /kentik/synthetics/dns 
WHERE target = 'google.com'  -- Won't work efficiently
```

**New Way (Tags):**
```sql
SELECT * FROM /kentik/synthetics/dns 
WHERE test_target = 'google.com'  -- Fast, indexed lookup
```

## Summary

The enhanced tag system provides:

✅ **Faster queries** - Tags are indexed  
✅ **Better filtering** - More precise target selection  
✅ **Flexible grouping** - Multi-dimensional analysis  
✅ **Easier troubleshooting** - Identify issues by configuration  
✅ **Richer context** - Understand what's being tested  

Use these tags to build powerful dashboards, create targeted alerts, and gain deeper insights into your synthetic testing infrastructure!

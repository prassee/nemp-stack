# Logging Framework - Quick Reference

## Overview
The ETL pipeline now includes comprehensive logging across all modules using Python's built-in `logging` module.

- **Console Output**: INFO level and above (user-facing)
- **File Output**: DEBUG level and above (troubleshooting)
- **Log File**: `./logs/etl.log` (single file, persistent)
- **Dependencies**: None (uses Python standard library)

## Files

### logger.py (New)
Centralized logging configuration module with two functions:
- `setup_logging()`: Initialize console + file handlers
- `get_logger(name)`: Get module-specific logger

### Updated Modules
- **backfill.py**: Logging for MySQL reads and Iceberg writes
- **setup_polaris.py**: Logging for Polaris catalog operations
- **main.py**: Logging initialization and command execution

## Usage

### Running Commands
```bash
# Console output shows INFO+ messages
python main.py backfill

# Detailed logs are saved to ./logs/etl.log
cat ./logs/etl.log
```

### Console Output Example
```
[2025-01-05 14:23:49] [INFO] etl.main - Starting backfill command...
[2025-01-05 14:23:50] [INFO] etl.backfill - Fetched 1,000,000 users from MySQL
[2025-01-05 14:24:15] [INFO] etl.backfill - Successfully exported 1,000,000 users
```

### File Log Example (./logs/etl.log)
```
[2025-01-05 14:23:49] [INFO] etl.main - Starting backfill command...
[2025-01-05 14:23:50] [DEBUG] etl.backfill - Connecting to Iceberg catalog via Polaris...
[2025-01-05 14:23:50] [INFO] etl.backfill - Successfully connected to Iceberg catalog
[2025-01-05 14:23:50] [DEBUG] etl.backfill - Checking if namespace 'analytics' exists...
[2025-01-05 14:23:51] [INFO] etl.backfill - Namespace 'analytics' already exists
[2025-01-05 14:24:15] [INFO] etl.backfill - Fetched 1,000,000 users from MySQL
[2025-01-05 14:24:45] [INFO] etl.backfill - Successfully exported 1,000,000 users to analytics.users
```

## Logging Levels

| Level | Usage | Where |
|-------|-------|-------|
| DEBUG | Internal details, schema info, API payloads | File only |
| INFO | Operations, milestones, success messages | Console + File |
| WARNING | Non-critical issues, deprecated features | Console + File |
| ERROR | Operation failures, exceptions | Console + File |
| CRITICAL | System-level failures | Console + File |

## How to Debug

### Issue: Command failed with unclear error
1. Check console output for INFO+ level error message
2. Check `./logs/etl.log` for full DEBUG details
3. Look for `logger.exception()` entries with full stack traces

### Issue: Understanding what happened during backfill
1. Run: `grep "INFO" ./logs/etl.log | tail -20`
2. Run: `grep "backfill" ./logs/etl.log` for table-specific logs

### Issue: Tracking API calls to Polaris
1. Run: `grep "DEBUG" ./logs/etl.log | grep "setup_polaris"`
2. Run: `grep "POST\|GET\|PUT\|DELETE" ./logs/etl.log`

## Format

All log entries follow this format:
```
[YYYY-MM-DD HH:MM:SS] [LEVEL] [etl.module.name] - Message
```

Example:
```
[2025-01-05 14:23:50] [INFO] etl.backfill - Fetched 1,000,000 users from MySQL
    │                      │               │              │
    │                      │               │              └─ Message
    │                      │               └─ Module name
    │                      └─ Log level
    └─ Timestamp
```

## Best Practices

### When Adding New Code
1. Import logging at the top: `import logging`
2. Initialize logger in module: `logger = logging.getLogger(__name__)`
3. Use appropriate level:
   - `logger.debug()` for internal details
   - `logger.info()` for user-facing operations
   - `logger.warning()` for issues that don't stop execution
   - `logger.error()` for failures
   - `logger.exception()` in except blocks for stack traces

### Example
```python
import logging

logger = logging.getLogger(__name__)

def fetch_data():
    logger.debug(f"Fetching from {url}")
    try:
        data = requests.get(url)
        logger.info(f"Fetched {len(data)} records")
        return data
    except Exception as e:
        logger.exception(f"Failed to fetch data: {e}")
        raise
```

## Limitations

Current implementation:
- Single log file (unbounded growth - user manages cleanup)
- Fixed to INFO level for console (not configurable)
- No log rotation

Future enhancements:
- Implement `RotatingFileHandler` for automatic log rotation
- Add CLI flag `--log-level` to configure console level
- Upgrade to `loguru` for JSON output and advanced features

## Troubleshooting

### Logs not appearing in ./logs/etl.log
1. Ensure logs directory exists: `ls -la ./logs/`
2. Check directory permissions: `chmod 755 ./logs/`
3. Run command from project root directory

### Too much console output
- This is by design - only INFO+ is shown
- Use `2>/dev/null` to suppress if needed: `python main.py backfill 2>/dev/null`

### Need to reset logs
```bash
rm ./logs/etl.log
# Next run will create a fresh log file
```

## Integration with Existing Code

### No breaking changes
- All existing functionality preserved
- `typer.echo()` still used for colored user output
- Logging is additive, not replacing user-facing output

### Backward compatible
- Can remove logging calls without breaking anything
- Can add more logging to any module independently
- No external dependencies required

---

**Commit Hash**: 100d3b7  
**Date Implemented**: 2025-01-05  
**Status**: Production Ready ✅

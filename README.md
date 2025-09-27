# Health Monitoring System

A comprehensive health monitoring system that tracks system metrics, generates alerts, and provides real-time monitoring capabilities.

## Features

- Real-time system metrics monitoring (CPU, Memory, Disk, Network)
- Automated alert generation with configurable thresholds
- RESTful API for data access
- WebSocket support for real-time updates
- Mock services for testing
- Web dashboard with live monitoring
- Component health monitoring
- Alert management and acknowledgment
- **Data retention and archiving system**
- **Persistent database storage**
- **Automated cleanup and archival**
- **Memory management with configurable retention policies**

## Project Structure

```
health-monitoring-system/
├── src/                    # Source code
│   ├── api/               # FastAPI application
│   ├── health/            # Health monitoring logic
│   ├── alerts/            # Alert management
│   ├── services/          # Background services
│   └── utils/             # Utility functions
├── database/              # Database models and connections
├── config/                # Configuration files
├── tests/                 # Test files
├── frontend/              # Frontend application
├── requirements.txt       # Python dependencies
├── start.sh              # Start all services
├── stop.sh               # Stop all services
├── test.sh               # Run tests
└── demo.sh               # Demo script
```

## Prerequisites

- Python 3.8+
- pip (Python package installer)

## Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd health-monitoring-system
   ```

2. **Set up Python environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the system**
   ```bash
   ./start.sh
   ```

4. **Run tests**
   ```bash
   ./test.sh
   ```

5. **Stop the system**
   ```bash
   ./stop.sh
   ```

## Development

### Running Tests
```bash
./test.sh
```

### Running Demo
```bash
./demo.sh
```

### Code Structure
- `src/` - Main application code
- `tests/` - Test suite
- `frontend/` - Web interface
- `config/` - Configuration files

## Configuration

Configuration files are located in the `config/` directory. Modify these files to customize the system behavior.

## API Documentation

The system provides a RESTful API for accessing health metrics and alerts. API documentation is available when the service is running.

### Available Endpoints

- `GET /` - API root
- `GET /health` - Overall system health status
- `GET /health/components` - Detailed component health information
- `GET /health/metrics` - System metrics history
- `GET /alerts` - Current alerts and alert summary
- `POST /alerts/{alert_id}/acknowledge` - Acknowledge a specific alert
- `POST /components/register` - Register a new component for monitoring
- `GET /dashboard` - Web dashboard interface
- `WS /ws` - WebSocket endpoint for real-time updates
- `POST /admin/retention/cleanup` - Manual data retention cleanup
- `GET /admin/retention/status` - Data retention status and policies

### WebSocket Events

The WebSocket endpoint broadcasts health updates every 5 seconds with the following structure:
```json
{
  "type": "health_update",
  "timestamp": "2025-09-25T16:18:13.515888",
  "health": {
    "overall_status": "healthy",
    "system_metrics": { ... },
    "components": { ... }
  },
  "alerts": {
    "active_alerts": 0,
    "critical_alerts": 0,
    "active_alert_list": []
  }
}
```

## Monitoring Features

### System Metrics
- CPU usage percentage
- Memory usage percentage
- Disk usage percentage
- Network I/O statistics
- Process count
- Load average (Unix/Linux)

### Component Health
- HTTP health check endpoints
- Response time monitoring
- Failure tracking
- Automatic status updates

### Alert System
- Configurable thresholds for CPU, Memory, and Disk usage
- Component availability alerts
- Alert acknowledgment and resolution
- Real-time alert broadcasting

### Data Retention & Archiving
- **Persistent database storage** - All metrics and alerts stored in SQLite database
- **Configurable retention policies** - Customizable data retention periods
- **Automated archiving** - Old data automatically archived and cleaned up
- **Memory management** - Keeps only recent data in memory for performance
- **Audit trail** - Complete log of all retention operations
- **Manual cleanup** - On-demand data cleanup via API endpoints

#### Retention Policies (Configurable)
- **System Metrics**: 30 days (configurable)
- **Component Health**: 7 days (configurable)
- **Alerts**: 90 days (configurable)
- **Cleanup Interval**: 24 hours (configurable)

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure ports 8000-8003 are available
2. **Dependencies not found**: Run `pip install -r requirements.txt`
3. **Services not starting**: Check logs in `api.log` and `mock_services.log`
4. **WebSocket connection failed**: Ensure the main API service is running

### Logs

- Main API logs: `api.log`
- Mock services logs: `mock_services.log`
- Process IDs: `api.pid`, `mock.pid`
- Database file: `health_monitoring.db`

### Data Retention Management

**Check retention status:**
```bash
curl http://localhost:8000/admin/retention/status
```

**Run manual cleanup:**
```bash
curl -X POST http://localhost:8000/admin/retention/cleanup
```

**View database:**
```bash
sqlite3 health_monitoring.db
.tables
SELECT COUNT(*) FROM system_metrics;
SELECT COUNT(*) FROM component_health;
SELECT COUNT(*) FROM alerts;
```

## Development

### Running in Development Mode

The application runs with auto-reload enabled by default. Any changes to the source code will automatically restart the server.

### Adding New Components

Use the `/components/register` endpoint to add new components for monitoring:

```bash
curl -X POST http://localhost:8000/components/register \
  -H "Content-Type: application/json" \
  -d '{
    "component_id": "my-service",
    "name": "My Service",
    "health_endpoint": "http://localhost:8080/health",
    "metadata": {"version": "1.0.0"}
  }'
```
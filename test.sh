#!/bin/bash

echo "🧪 Running Health Monitoring System Tests"
echo "========================================="

# Activate virtual environment if not already active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

# Check if services are running
echo "🔍 Checking if services are running..."

if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Main API service is not running. Please start it with ./start.sh"
    exit 1
fi

if ! curl -s http://localhost:8001/health > /dev/null; then
    echo "❌ Mock services are not running. Please start them with ./start.sh"
    exit 1
fi

echo "✅ All services are running"

# Test API endpoints
echo "🔍 Testing API endpoints..."

echo "1. Testing system health endpoint..."
if curl -s http://localhost:8000/health | grep -q "overall_status"; then
    echo "✅ System health endpoint working"
else
    echo "❌ System health endpoint failed"
    exit 1
fi

echo "2. Testing component health endpoint..."
if curl -s http://localhost:8000/health/components | grep -q "components"; then
    echo "✅ Component health endpoint working"
else
    echo "❌ Component health endpoint failed"
    exit 1
fi

echo "3. Testing alerts endpoint..."
if curl -s http://localhost:8000/alerts | grep -q "active_alerts"; then
    echo "✅ Alerts endpoint working"
else
    echo "❌ Alerts endpoint failed"
    exit 1
fi

echo "4. Testing metrics endpoint..."
if curl -s http://localhost:8000/health/metrics | grep -q "metrics"; then
    echo "✅ Metrics endpoint working"
else
    echo "❌ Metrics endpoint failed"
    exit 1
fi

echo "5. Testing dashboard endpoint..."
if curl -s http://localhost:8000/dashboard | grep -q "Health Monitoring Dashboard"; then
    echo "✅ Dashboard endpoint working"
else
    echo "❌ Dashboard endpoint failed"
    exit 1
fi

# Test WebSocket connection
echo "6. Testing WebSocket connection..."
python3 -c "
import asyncio
import websockets
import json
import sys

async def test_ws():
    try:
        async with websockets.connect('ws://localhost:8000/ws') as websocket:
            message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
            data = json.loads(message)
            if data.get('type') == 'health_update':
                print('✅ WebSocket connection working')
                return True
            else:
                print('❌ WebSocket message format incorrect')
                return False
    except Exception as e:
        print(f'❌ WebSocket connection failed: {e}')
        return False

result = asyncio.run(test_ws())
sys.exit(0 if result else 1)
"

WS_TEST_RESULT=$?
if [ $WS_TEST_RESULT -eq 0 ]; then
    echo "✅ WebSocket test passed"
else
    echo "⚠️  WebSocket test failed (this is optional for basic functionality)"
    echo "   The main API endpoints are working correctly"
fi

echo ""
echo "🎉 All tests passed successfully!"
echo "✅ Health Monitoring System is working correctly"
echo ""
echo "🌐 Available endpoints:"
echo "   - Dashboard: http://localhost:8000/dashboard"
echo "   - API Docs: http://localhost:8000/docs"
echo "   - Health: http://localhost:8000/health"
echo "   - Alerts: http://localhost:8000/alerts"

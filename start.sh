#!/bin/bash

echo "🏥 Starting Health Monitoring System..."

# Check if services are already running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  Health Monitoring System is already running!"
    echo "📊 Dashboard: http://localhost:8000/dashboard"
    echo "🔍 API Health: http://localhost:8000/health"
    echo "📋 API Docs: http://localhost:8000/docs"
    echo "🛑 Use ./stop.sh to stop the services first if you want to restart"
    exit 0
fi

# Activate virtual environment if not already active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    source venv/bin/activate
fi

# Start mock services in background with proper output redirection
echo "🔧 Starting mock services..."
nohup python src/utils/mock_services.py > mock_services.log 2>&1 &
MOCK_PID=$!

# Wait for mock services to start
echo "⏳ Waiting for mock services to initialize..."
sleep 5

# Check if mock services started successfully
if ! ps -p $MOCK_PID > /dev/null 2>&1; then
    echo "❌ Failed to start mock services. Check mock_services.log for details."
    exit 1
fi

# Start main application
echo "🚀 Starting health monitoring API..."
nohup python3 -m src.api.main > api.log 2>&1 &
API_PID=$!

# Wait for API to start
echo "⏳ Waiting for API to initialize..."
sleep 10

# Check if API started successfully
if ! ps -p $API_PID > /dev/null 2>&1; then
    echo "❌ Failed to start API service. Check api.log for details."
    # Kill mock services if API failed
    kill $MOCK_PID 2>/dev/null || true
    exit 1
fi

# Verify API is responding
echo "🔍 Verifying API is responding..."
for i in {1..5}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is responding successfully"
        break
    fi
    if [ $i -eq 5 ]; then
        echo "❌ API is not responding after 5 attempts. Check api.log for details."
        kill $API_PID $MOCK_PID 2>/dev/null || true
        exit 1
    fi
    echo "⏳ Waiting for API to respond... (attempt $i/5)"
    sleep 2
done

echo "✅ Health Monitoring System started!"
echo "📊 Dashboard: http://localhost:8000/dashboard"
echo "🔍 API Health: http://localhost:8000/health"
echo "📋 API Docs: http://localhost:8000/docs"

# Store PIDs for stop script
echo $MOCK_PID > mock.pid
echo $API_PID > api.pid

echo "💡 Use ./stop.sh to stop all services"
echo "🔄 Services will run in background..."
echo "📝 Check mock_services.log and api.log for service output"
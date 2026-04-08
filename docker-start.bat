@echo off
REM Build and run Docker containers for local development

echo ============================================
echo Medical Chatbot - Docker Setup
echo ============================================
echo.

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create .env file with:
    echo   GROQ_API_KEY=your_key_here
    echo.
    pause
    exit /b 1
)

REM Check if vector database exists
if not exist data\vector_store.index (
    echo Building vector database...
    python app\db\ingest.py
    echo Vector database created
    echo.
)

REM Build and start containers
echo Building Docker images...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

echo.
echo ============================================
echo Services Started Successfully!
echo ============================================
echo.
echo Service URLs:
echo   - API:          http://localhost:8000
echo   - RabbitMQ UI:  http://localhost:15672 (guest/guest)
echo.
echo Useful commands:
echo   - View logs:    docker-compose logs -f
echo   - Stop:         docker-compose down
echo   - Restart:      docker-compose restart
echo.
echo Test the API:
echo   curl -X POST http://localhost:8000/chat ^
echo     -H "Content-Type: application/json" ^
echo     -d "{\"message\":\"wound hurts\",\"pain_level\":5,\"discomfort_level\":4}"
echo.
pause

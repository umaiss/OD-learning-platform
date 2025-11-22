#!/bin/bash
# Helper script to run backend commands with the correct Python interpreter

set -e

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Please run: python -m venv venv"
    exit 1
fi

# Use venv's Python
PYTHON="./venv/bin/python"

# Parse command
case "$1" in
    init-db)
        echo "Initializing database..."
        $PYTHON db/init_db.py
        ;;
    seed)
        echo "Seeding database..."
        $PYTHON seeds/seed_data.py
        ;;
    test)
        echo "Running tests..."
        ./venv/bin/pytest "${@:2}"
        ;;
    server)
        echo "Starting server..."
        ./venv/bin/uvicorn main:app --reload --host 0.0.0.0 --port 8000
        ;;
    *)
        echo "Usage: ./run.sh {init-db|seed|test|server} [options]"
        echo ""
        echo "Commands:"
        echo "  init-db    Initialize database (create tables)"
        echo "  seed       Seed database with demo data"
        echo "  test       Run tests (pass pytest options after 'test')"
        echo "  server     Start the development server"
        echo ""
        echo "Examples:"
        echo "  ./run.sh init-db"
        echo "  ./run.sh seed"
        echo "  ./run.sh test tests/test_agents.py -v"
        echo "  ./run.sh server"
        exit 1
        ;;
esac


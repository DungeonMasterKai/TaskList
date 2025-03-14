#!/bin/bash

PID_FILE="$HOME/.autorun.pid"
LOG_FILE="$HOME/autorun.log"

start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Script is already running (PID: $PID)"
            exit 1
        else
            echo "Stale PID file detected. Removing..."
            rm -f "$PID_FILE"
        fi
    fi

    echo "Starting autorun..."
    nohup bash "$0" run >> "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    echo "Autorun started (PID: $(cat $PID_FILE))"
}

stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "No running process found."
        exit 1
    fi

    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "Stopping autorun (PID: $PID)..."
        kill "$PID"
    else
        echo "Process not found. Removing stale PID file."
    fi
    rm -f "$PID_FILE"
    echo "Autorun stopped."
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo "Autorun is running (PID: $PID)"
        else
            echo "Autorun is NOT running, but PID file exists (stale PID: $PID)."
            rm -f "$PID_FILE"
            echo "Stale PID file removed."
        fi
    else
        echo "Autorun is not running."
    fi
}

run() {
    echo "Running autorun process..."
    
    LAST_SUCCESS_DATE=""
    
    schedule() {
        DAY_OF_WEEK=$(date +%u)
        CURRENT_DATE=$(date +'%Y-%m-%d')
        CURRENT_HOUR=$(date +'%H')

        if [[ "$DAY_OF_WEEK" -ge 6 ]]; then
            echo "Weekend, skip"
            return 1
        fi

        if [[ "10$CURRENT_HOUR" -ge 10 && "$CURRENT_DATE" != "$LAST_SUCCESS_DATE" ]]; then
            echo "Running automark for $CURRENT_DATE"
            return 0
        else
            echo "Waiting: $CURRENT_HOUR..."
            return 1
        fi
    }

    trap 'rm -f "$PID_FILE"; exit' SIGINT SIGTERM

    while true; do
        if [[ -f stop_automark ]]; then
            echo "STOPPING AUTOMARK"
            rm -f "$PID_FILE"
            break
        fi

        if schedule; then
            echo "Running command"
            python run_compare.py config/k2_decommission/setting.json
            LAST_SUCCESS_DATE="$CURRENT_DATE"
        fi

        sleep 600
    done
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    status)
        status
        ;;
    run)
        run
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
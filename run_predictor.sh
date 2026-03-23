#!/bin/bash

# --- CONFIGURATION (Change these) ---
PREDICTOR_VERSION="1.8.0"

# --- HELP CHECK ---
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    docker run --rm wearablepermed-predictor:$PREDICTOR_VERSION --help
    exit 0
fi

# Checks if there are at least 3 arguments provided
if [ "$#" -lt 3 ]; then
    echo "❌ Error: Missing mandatory arguments."
    echo "Usage: ./run_predictor.sh <MODEL_ID> <RESOURCE_ID> <PRED_FOLDER> [OPTIONAL_FLAGS]"
    echo ""
    echo "Example (Mandatory only):"
    echo "  ./run_predictor.sh MODEL_PI_RF_ACC_GYR_15 /data/data.csv /results"
    echo ""
    echo "Example (With Optionals):"
    echo "  ./run_predictor.sh MODEL_PI_RF_ACC_GYR_15 /data/data.csv /results --is-label-text -v"
    exit 1
fi

# Assign Mandatory Positional Arguments
MODEL_ID=$1
RESOURCE_ID=$2
PRED_FOLDER=$3

# Remove the first 3 arguments from the list so "$@" contains only the rest
shift 3

# --- GENERATE UNIQUE NAME ---
# Format: MODELNAME_YYYYMMDD_HHMMSS_RAND
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
UNIQUE_ID=$((1 + $RANDOM % 1000))
CONTAINER_NAME="${MODEL_ID}_${TIMESTAMP}_${UNIQUE_ID}"

# --- EXECUTION ---
echo "🚀 Starting Wearable Predictor Container (v$PREDICTOR_VERSION)..."

docker run --rm \
  --name "$CONTAINER_NAME" \
  -u $(id -u):$(id -g) \
  -v "$RESOURCE_ID":"$RESOURCE_ID" \
  -v "$PRED_FOLDER":"$PRED_FOLDER" \
  wearablepermed-predictor:"$PREDICTOR_VERSION" \
  --model-id "$MODEL_ID" \
  --resource-id "$RESOURCE_ID" \
  --prediction-folder "$PRED_FOLDER" \
  "$@"

echo "✅ Prediction complete. Check results in: $PRED_FOLDER"
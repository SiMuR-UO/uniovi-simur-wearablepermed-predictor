#!/bin/bash

# --- CONFIGURATION (Change these) ---
PREDICTOR_VERSION="1.17.0"

# --- HELP CHECK ---
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    docker run --rm wearablepermed-predictor:$PREDICTOR_VERSION --help
    exit 0
fi

# Checks if there are at least 5 arguments provided
if [ "$#" -lt 5 ]; then
    echo "❌ Error: Missing mandatory arguments."
    echo "Usage: ./run_predictor.sh <MODELS_FOLDER> <MODEL_ID> <RESOURCES_FOLDER> <RESOURCE_ID> <CASES_FOLDER> [OPTIONAL_ARGUMENTS]"
    echo ""
    echo "Example (Mandatory only):"
    echo "  ./run_predictor.sh /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/models MODEL_PI_RF_ACC_GYR_15 /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input case_PI_BRF_acc_gyr_01/PMP1024_W1_PI_1.csv /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output"
    echo ""
    echo "Example (With Optionals):"
    echo "  ./run_predictor.sh /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/models MODEL_PI_RF_ACC_GYR_15 /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/input case_PI_BRF_acc_gyr_01/PMP1024_W1_PI_1.csv /home/miguel/git/uniovi/simur/uniovi-simur-wearablepermed-predictor/data/output case_PI_BRF_acc_gyr_4_classes_01 --verbose"
    exit 1
fi

# Assign Mandatory Positional Arguments
MODELS_FOLDER=$1
MODEL_ID=$2
RESOURCES_FOLDER=$3
RESOURCE_ID=$4
CASES_FOLDER=$5

# Remove the first 5 arguments from the list so "$@" contains only the rest
shift 5

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
  -v "$MODELS_FOLDER":"$MODELS_FOLDER" \
  -v "$RESOURCES_FOLDER":"$RESOURCES_FOLDER" \
  -v "$CASES_FOLDER":"$CASES_FOLDER" \
  wearablepermed-predictor:"$PREDICTOR_VERSION" \
  --models-folder "$MODELS_FOLDER" \
  --model-id "$MODEL_ID" \
  --resources-folder "$RESOURCES_FOLDER" \
  --resource-id "$RESOURCE_ID" \
  --cases-folder "$CASES_FOLDER" \
  "$@"

echo "✅ Prediction complete. Check results in: $CASES_FOLDER"
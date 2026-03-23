@echo off
setlocal

:: --- SYSTEM CONFIGURATION ---
set PREDICTOR_VERSION=1.8.0

:: --- HELP CHECK ---
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
goto :validate

:show_help
docker run --rm wearablepermed-predictor:%PREDICTOR_VERSION% --help
pause
exit /b 0

:validate
:: Check for 3 mandatory arguments
if "%~3"=="" (
    echo ❌ Error: Missing mandatory arguments.
    echo Usage: run_predictor.bat [MODEL_ID] [RESOURCE_ID] [PRED_FOLDER]
    pause
    exit /b 1
)

:: Assign Mandatory
set MODEL_ID=%1
set RESOURCE_ID=%2
set PRED_FOLDER=%3

:: Shift the internal pointer to capture remaining arguments
shift
shift
shift

:: --- GENERATE UNIQUE NAME ---
:: Get Date/Time in a safe format (YYYYMMDD_HHMMSS)
set t=%time: =0%
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%t:~0,2%%t:~3,2%%t:~6,2%
set UNIQUE_ID=%RANDOM%
set CONTAINER_NAME=%M_MODEL_ID%_%TIMESTAMP%_%UNIQUE_ID%

:: %1 now starts from the 4th argument provided by the user
echo 🚀 Initializing Docker Predictor...

docker run --rm ^
  --name "%CONTAINER_NAME%" ^
  -u $(id -u):$(id -g) ^
  -v "$RESOURCE_ID":"$RESOURCE_ID" ^
  -v "$PRED_FOLDER":"$PRED_FOLDER" ^
  wearablepermed-predictor:%PREDICTOR_VERSION% ^
  --model-id %MODEL_ID% ^
  --resource-id %RESOURCE_ID% ^
  --prediction-folder %PRED_FOLDER% ^
  %1 %2 %3 %4 %5

pause
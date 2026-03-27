@echo off
setlocal

:: --- SYSTEM CONFIGURATION ---
set PREDICTOR_VERSION=1.18.0

:: --- HELP CHECK ---
if "%~1"=="-h" goto :show_help
if "%~1"=="--help" goto :show_help
goto :validate

:show_help
docker run --rm wearablepermed-predictor:%PREDICTOR_VERSION% --help
pause
exit /b 0

:validate
:: Check for 5 mandatory arguments
if "%~5"=="" (
    echo ❌ Error: Missing mandatory arguments.
    echo Usage: run_predictor.bat [MODELS_FOLDER] [MODEL_ID] [RESOURCES_FOLDER] [RESOURCE_ID] [CASES_FOLDER] [OPTIONAL_ARGUMENTS]
    pause
    exit /b 1
)

:: Assign Mandatory
set MODELS_FOLDER=%1
set MODEL_ID=%2
set RESOURCES_FOLDER=%3
set RESOURCE_ID=%4
set CASES_FOLDER=%5

:: Shift the internal pointer to capture remaining arguments
shift
shift
shift
shift
shift

:: --- GENERATE UNIQUE NAME ---
:: Get Date/Time in a safe format (YYYYMMDD_HHMMSS)
set t=%time: =0%
set TIMESTAMP=%date:~10,4%%date:~4,2%%date:~7,2%_%t:~0,2%%t:~3,2%%t:~6,2%
set UNIQUE_ID=%RANDOM%
set CONTAINER_NAME=%MODEL_ID%_%TIMESTAMP%_%UNIQUE_ID%

:: %1 now starts from the 4th argument provided by the user
echo 🚀 Initializing Docker Predictor...

docker run --rm ^
  --name "%CONTAINER_NAME%" ^
  -u $(id -u):$(id -g) ^
  -v "$MODELS_FOLDER":"$MODELS_FOLDER" ^
  -v "$RESOURCES_FOLDER":"$RESOURCES_FOLDER" ^
  -v "$CASES_FOLDER":"$CASES_FOLDER" ^
  wearablepermed-predictor:%PREDICTOR_VERSION% ^
  --models-folder %MODELS_FOLDER% ^
  --model-id %MODEL_ID% ^
  --resources-folder %RESOURCES_FOLDER% ^
  --resource-id %RESOURCE_ID% ^
  --cases-folder %CASES_FOLDER% ^
  %1 %2 %3 %4 %5

pause
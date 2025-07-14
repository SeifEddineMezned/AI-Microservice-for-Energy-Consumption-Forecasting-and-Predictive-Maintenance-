@echo off
echo Energy Forecasting System Launcher
echo ===============================
echo Choose an option:
echo 1. Install dependencies
echo 2. Train models
echo 3. Run predictions (command line)
echo 4. Start API server
echo 5. Run API examples
echo 6. Exit
echo.

set /p choice=Enter your choice (1-6): 

if "%choice%"=="1" goto install
if "%choice%"=="2" goto train
if "%choice%"=="3" goto predict
if "%choice%"=="4" goto api
if "%choice%"=="5" goto examples
if "%choice%"=="6" goto end

echo Invalid choice. Please try again.
echo.
goto menu

:install
echo.
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Dependencies installed successfully.
echo.
pause
goto menu

:train
echo.
echo Training models...
python train_model.py
echo.
pause
goto menu

:predict
echo.
echo Running predictions...
python predict.py
echo.
pause
goto menu

:api
echo.
echo Starting API server...
echo The server will run on port 8000 until you press Ctrl+C to stop it.
echo.
python main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error: Could not start server on port 8000. The port may already be in use.
    echo Please ensure no other applications are using port 8000 before trying again.
    echo.
    pause
)
goto menu

:examples
echo.
echo Running API examples...
echo Make sure the API server is running in another terminal window.
echo.
python api_examples.py
echo.
pause
goto menu

:end
echo.
echo Thank you for using the Energy Forecasting System.
echo.
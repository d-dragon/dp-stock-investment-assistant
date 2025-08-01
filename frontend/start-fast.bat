@echo off
echo 🚀 Starting React app with optimizations...
echo ⚡ Fast mode enabled - No source maps, optimized for speed

REM Set performance environment variables
set GENERATE_SOURCEMAP=false
set FAST_REFRESH=true
set TSC_COMPILE_ON_ERROR=true
set ESLINT_NO_DEV_ERRORS=true
set SKIP_PREFLIGHT_CHECK=true
set BROWSER=none
set NODE_OPTIONS=--max_old_space_size=4096

REM Clean cache if needed
if exist "node_modules\.cache" (
    echo 🧹 Cleaning cache...
    rmdir /s /q "node_modules\.cache"
)

echo ⏰ Starting at %time%
npm start

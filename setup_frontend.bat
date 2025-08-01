@echo off
echo Setting up React frontend...

if not exist "frontend" (
    echo Creating React application...
    npx create-react-app frontend --template typescript
) else (
    echo Frontend directory already exists.
)

cd frontend

echo Installing additional dependencies...
npm install socket.io-client axios @mui/material @emotion/react @emotion/styled @mui/icons-material

echo.
echo Frontend setup complete!
echo To start the frontend: cd frontend && npm start
echo The React app will be available at http://localhost:3000

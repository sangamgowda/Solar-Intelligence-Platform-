# setup_env.ps1
# This script ensures Python and Node.js are installed and sets up the project dependencies.

$ErrorActionPreference = "Continue" # Don't stop on minor errors like "already installed"

function Write-Status ($msg, $color = "Cyan") {
    Write-Host "`n>>> $msg" -ForegroundColor $color
}

Write-Status "Starting Sola Project Trichy Environment Setup..." "White"

# 1. Check/Install Winget
if (!(Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Status "ERROR: Winget not found. Please install 'App Installer' from the Microsoft Store." "Red"
    Write-Status "https://apps.microsoft.com/store/detail/python/9NBLGGH4LNNG" "Blue"
    exit 1
}

# 2. Check/Install Python 3.11
try {
    $pythonCheck = Get-Command python -ErrorAction SilentlyContinue
    if (!$pythonCheck) {
        Write-Status "Python not found. Installing Python 3.11 via Winget..." "Yellow"
        winget install --id Python.Python.3.11 --exact --accept-package-agreements --accept-source-agreements
        # Attempt to refresh path for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Status "Python is already installed: $($pythonCheck.Source)" "Green"
    }
} catch {
    Write-Status "Failed to install Python. Please install it manually from python.org" "Red"
}

# 3. Check/Install Node.js LTS
try {
    $nodeCheck = Get-Command node -ErrorAction SilentlyContinue
    if (!$nodeCheck) {
        Write-Status "Node.js not found. Installing Node.js LTS via Winget..." "Yellow"
        winget install --id OpenJS.NodeJS.LTS --exact --accept-package-agreements --accept-source-agreements
        # Attempt to refresh path for current session
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    } else {
        Write-Status "Node.js is already installed: $($nodeCheck.Source)" "Green"
    }
} catch {
    Write-Status "Failed to install Node.js. Please install it manually from nodejs.org" "Red"
}

# 4. Backend Setup
Write-Status "Setting up Backend (Python)..."

$pythonCmd = "python"
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        $pythonCmd = "py"
    } else {
        Write-Status "ERROR: Python not found even after attempt to install. Please restart your terminal or install manually." "Red"
        exit 1
    }
}

if (!(Test-Path "backend/venv")) {
    Write-Status "Creating Virtual Environment in backend/venv using $pythonCmd..." "Gray"
    & $pythonCmd -m venv backend/venv
}

Write-Status "Installing/Updating Python dependencies..." "Gray"
& "backend/venv/Scripts/python.exe" -m pip install --upgrade pip
& "backend/venv/Scripts/python.exe" -m pip install -r backend/requirements.txt

# 5. Frontend Setup
Write-Status "Setting up Frontend (Node.js)..."
if (Test-Path "frontend") {
    Push-Location frontend
    if (!(Test-Path "node_modules")) {
        Write-Status "Installing Node dependencies (npm install)..." "Gray"
        npm install
    } else {
        Write-Status "Node modules already present. Skipping install." "Green"
    }
    Pop-Location
} else {
    Write-Status "ERROR: frontend directory not found!" "Red"
}

Write-Status "Setup Complete! Everything is ready to run." "Green"

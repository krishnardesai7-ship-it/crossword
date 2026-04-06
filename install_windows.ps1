$ErrorActionPreference = "Stop"

Write-Host "Upgrading pip tooling..."
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing project dependencies..."
python -m pip install -r "$PSScriptRoot\requirement.txt"

Write-Host "Installing face_recognition_models from GitHub..."
if (Get-Command git -ErrorAction SilentlyContinue) {
    python -m pip install git+https://github.com/ageitgey/face_recognition_models
}
else {
    Write-Host "Git is not in PATH. Installing from GitHub ZIP instead..."
    python -m pip install https://github.com/ageitgey/face_recognition_models/archive/refs/heads/master.zip
}

Write-Host "Installing face-recognition without pulling dlib source build..."
python -m pip install --no-deps face-recognition==1.3.0

Write-Host "Done."

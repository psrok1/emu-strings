curl \
    -F "engine=JScript" \
    -F "emulator=WinedropEmulator" \
    -F "file=@test.js" \
    http://localhost:5000/api/submit

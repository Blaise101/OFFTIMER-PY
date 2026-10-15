# Shutdown Timer — Build Instructions

## 1. About
Shutdown Timer is a small floating Windows application built with Python and Tkinter. It allows you to schedule or cancel a computer shutdown using a countdown or a specific time.

## 2. Requirements
- Windows 10 or Windows 11
- Python 3 installed
- The original Python source file: `shutdown_timer.py`
- Internet connection to install PyInstaller

## 3. Install PyInstaller
Open Command Prompt and run:

```bash
python -m pip install pyinstaller
```

If `python` doesn't work, try:

```bash
py -m pip install pyinstaller
```

## 4. Build the EXE
Open Command Prompt in the folder containing `shutdown_timer.py`.

Run:

```bash
python -m PyInstaller --onefile --noconsole --name offtimer shutdown_timer.py
```

Alternatively, use `py` instead of `python` if necessary.

## 5. Find the Executable
After the build finishes, find the application here:

`dist\offtimer.exe`

Copy this file to your preferred location, such as your Desktop.

You can double-click it to launch the application without opening VS Code or installing Python separately on the target computer.

## 6. Cleanup
The following files and folders are generated during the build:
- `build\`
- `dist\`
- `offtimer.spec`

You can delete the build files after confirming that the executable works. Keep the original `shutdown_timer.py` somewhere safe so you can rebuild or modify the application later.

## 7. Important Notes
- Rebuild the executable whenever you modify the Python source code.
- Keep a backup of `shutdown_timer.py`.
- The executable may trigger Windows security warnings because it is not digitally signed.
- The application schedules shutdowns through Windows. Closing the application does not necessarily cancel a scheduled shutdown.
- Test the application before relying on it.

## Quick Build Command

```bash
python -m PyInstaller --onefile --noconsole --name offtimer shutdown_timer.py
```

**Output:** `dist\offtimer.exe`


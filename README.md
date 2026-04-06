# Django Face Login System
Face Login System with Django 
<p align="center">
  <img align="center" src="https://github.com/omarreda22/django-face-login-system/blob/main/src/core/static/git_face_register-min.gif">
</p>

## In This Project:
- Login with face
- Sending SMS mobile message after register
- Sending email message by celery after register
- Celery schedules

## Windows Setup (fix for dlib wheel error)
Use Python 3.11 (64-bit), then run:

```powershell
cd src
..\install_windows.ps1
```

If PowerShell blocks script execution, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\install_windows.ps1
```

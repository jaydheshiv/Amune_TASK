@echo off
echo Setting up environment files...
if not exist .env (
    if exist .env.example (
        copy .env.example .env >nul
        echo Created .env from .env.example template.
    )
)
echo Setting up backend...
python -m venv env
call env\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
echo Setting up frontend...
cd frontend
npm install
cd ..
echo Setup complete.

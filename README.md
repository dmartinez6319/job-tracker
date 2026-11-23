# job-tracker

## Database Schema Setup ##
1. Navigate to project's root directory and run the command below to initialize the database
```bash
mysql -u root -p < schema.sql
```

## Backend Setup ##
1. Setup python virtual environment
```bash
python -m venv .venv
```
2. activate environment
```bash
source .venv/Scripts/activate
```
3. install flask and mysql dependecies
```bash
python -m pip install flask mysql-connector-python python-dotenv
```
4. start the server
```bash
python app.py
```
5. open up the local website
```bash
http://127.0.0.1:5000
```

# FromHome

![Python 3.13.1](https://img.shields.io/badge/Python-3.13-blue?logo=python)  
![Flask 1.3.1](https://shields.io/badge/Flask-1.3.1-blue?logo=flask&logoColor=white)


FromHome is a web-based college delivery system for general items, food, etc. that 
utilizes volunteer work to create an environment that favors both parents and students.

### Access the live website [here](fromhome.pythonanywhere.com).

# Features
- **Up-to-date Database:** Adds deliveries to the list and clears old ones immediately in order to ensure a smooth experience
- **ZIP Code filtering:** Allows filtering of deliveries by ZIP code so that results are more relevant
- **Reservation system:** Runs on a first-come first-serve reservation system to avoid packed deliveries
- **Email confirmation system:** Sends an email to your email address with details when the delivery is created, if a volunteer edits a trip you signed up for, etc.
- **Modern, clean UI:** Utilizes a fast search button and an at-a-glance delivery table, among other smooth design elements

# Running/Installation

**The site is available 24/7 [here](fromhome.pythonanywhere.com) on Pythonanywhere.**  

You don't need to do any local installation for this; it is possible to run this project locally, but it will not be connected to the main database. Here's how to do it:

### 1. Clone the Repository
```bash
git clone https://github.com
cd your-repo-name
```

### 2. Configure Your Virtual Environment
Create your own local environment for packages, databases, etc.
```bash
python -m venv venv

# Activate on Linux/macOS:
source venv/bin/activate

# Activate on Windows:
venv\Scripts\activate
```

### 3. Install Package Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Initialize your SQL Database
You'll need to create an SQL database that matches the internal structure.
Initialize these tables into the database:
- DELIVERIES
- INDIVIDUALS
- VERIFY (not currently used but will in the future)


### 5. Configure Environment Variables
Duplicate the example configurations file and assign your own application secrets:
```bash
cp .env.example .env
```
Open the newly created `.env` file and populate your parameters, including your SQL database details.

Note that a CSV filled with all US universities is provided, in `/mysite/static`, so you may add that to `.env` if you like or use your own if you have one.

### 6. Start the Development Server
```bash
python run.py
```

# Project Structure

```text
├── app/
│   ├── __init__.py          # Application configuration
│   ├── routes.py            # Web view routes and GET/POST methods
│   ├── EmailSender.py       # Sends emails to users via SMTP
│   ├── SQLFunctions.py      # Handles MySQL operations for the website
│   ├── static/              # CSS, client-side JavaScript, and image asset files
│   └── templates/           # Jinja2 HTML layout templates
├── .env.example             # Template for secure environment flags
├── requirements.txt         # Package dependencies list
└── run.py                   # Main development server execution gateway
```

## 📄 License

Distributed under the terms of the MIT License. Check out the `LICENSE` file for more concrete legal information.

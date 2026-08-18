# FromHome

![Python 3.13.1](https://img.shields.io/badge/Python-3.13-blue?logo=python)  
![Flask 1.3.1](https://shields.io/badge/Flask-1.3.1-blue?logo=flask&logoColor=white)


FromHome is a web-based college delivery system for general items, food, etc. that 
utilizes volunteer work to create an environment that favors both parents and students.

# Features
- **Up-to-date Database:** Adds deliveries to the list and clears old ones immediately in order to ensure a smooth experience
- **ZIP Code filtering:** Allows filtering of deliveries by ZIP code so that results are more relevant
- **Reservation system:** Runs on a first-come first-serve reservation system to avoid packed deliveries
- **Email confirmation system:** Sends an email to your email address with details when the delivery is created, if a volunteer edits a trip you signed up for, etc.
- **Modern, clean UI:** Utilizes a fast search button and an at-a-glance delivery table, among other smooth design elements

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

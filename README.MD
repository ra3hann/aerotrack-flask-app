# AeroTrack - Airline Management System ✈️

AeroTrack is a full-featured web application built with Flask for managing flights, passengers, and shipments. This project was developed as part of the AI Campus Assignment and demonstrates a complete, deployable web service with a modern user interface and full CRUD functionality.

The live, deployed application can be accessed here: **[Your Render App Link]**

---

## Key Features

* **Full CRUD Functionality**: Create, Read, Update, and Delete operations for Flights, Passengers, and Shipments.
* **Secure User Authentication**: A complete user registration and login system protects all data management pages.
* **Modern Dark-Mode UI**: A sleek, professional, and consistent user interface across the entire application, designed for clarity and ease of use.
* **Dynamic Data Management**:
    * **Search**: Passengers can be easily found using a name-based search filter.
    * **Status Tracking**: Flights have a color-coded status (e.g., Scheduled, On Time, Delayed) for at-a-glance monitoring.
* **Business Logic Implementation**: Includes a calculated field for dynamically determining total shipment costs based on weight and fees.

---

## Tech Stack 🛠️

* **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Bcrypt
* **Database**: SQLite
* **Frontend**: HTML, embedded CSS
* **Server**: Gunicorn
* **Deployment**: Render

---

## How to Run Locally

### 1. Clone the repository:
```sh
git clone [https://github.com/ra3hann/aerotrack-flask-app.git](https://github.com/ra3hann/aerotrack-flask-app.git)

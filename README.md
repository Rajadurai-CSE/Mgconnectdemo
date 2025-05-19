# MigrantConnect TN

A comprehensive platform for migrant workers in Tamil Nadu ensuring smooth registration, effective tracking, and complete support.

## Project Overview

MigrantConnect TN is a web application designed to address key challenges faced by migrant workers in Tamil Nadu by creating a robust platform that ensures smooth registration, effective tracking, and comprehensive support tailored to their needs.

### Key Features

- **Registration & Unique ID**: Easy registration process with document verification and unique ID generation
- **Effective Tracking**: Track employment details across sectors and maintain accurate workforce records
- **Support System**: Dedicated support system to address challenges with real-time query tracking
- **Multilingual Support**: Platform supports multiple languages for accessibility
- **Community Support**: Connect with others in similar industries to enhance networks
- **Schemes & Policies**: Customized recommendations for government schemes and policies

## User Roles

1. **Migrants**
   - Registration with supporting documents
   - Document verification and UUID generation
   - Access to latest schemes and policies
   - Support request submission
   - View job opportunities
   - Connect with other migrants in similar jobs

2. **Employers**
   - Company profile management
   - Post job opportunities
   - Add migrant worker details
   - Track migrant employee records

3. **Admin**
   - Approve migrant registrations
   - Manage support requests
   - Release new policies (sector-specific or general)
   - Monitor platform statistics

## Technical Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: Bootstrap 5, Jinja Templates, JavaScript
- **Authentication**: Flask-Login

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- MongoDB (local or Atlas)
- Git

### Installation Steps

1. Clone the repository:
   ```
   git clone <repository-url>
   cd MigrantConnectTN
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate  # On Windows
   source venv/bin/activate  # On Unix or MacOS
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your_secret_key_here
   MONGO_URI=mongodb://localhost:27017/migrantconnect
   ```

5. Create an `uploads` directory:
   ```
   mkdir app/static/uploads
   ```

6. Run the application:
   ```
   python run.py
   ```

7. Access the application at `http://localhost:5000`

## Default Admin Account

To create an admin account, use the MongoDB shell or a MongoDB GUI tool to insert an admin user:

```javascript
db.users.insertOne({
  email: "admin@migrantconnect.gov.in",
  password: "pbkdf2:sha256:260000$hashed_password_here",
  role: "admin",
  created_at: new Date()
})
```

Replace "hashed_password_here" with an appropriate password hash. You can generate one using the Werkzeug library in Python.

## Project Structure

```
MigrantConnectTN/
│
├── app/                    # Main application package
│   ├── __init__.py         # Application factory
│   ├── models/             # Data models
│   │   └── users.py        # User, Migrant, Employer models
│   │
│   ├── routes/             # Route handlers
│   │   ├── admin.py        # Admin routes
│   │   ├── auth.py         # Authentication routes
│   │   ├── employers.py    # Employer routes
│   │   ├── main.py         # Main routes
│   │   └── migrants.py     # Migrant routes
│   │
│   ├── static/             # Static files
│   │   ├── css/            # CSS files
│   │   ├── js/             # JavaScript files
│   │   ├── images/         # Image files
│   │   └── uploads/        # User uploads
│   │
│   └── templates/          # Jinja templates
│       ├── admin/          # Admin templates
│       ├── auth/           # Authentication templates
│       ├── employers/      # Employer templates
│       ├── main/           # Main templates
│       ├── migrants/       # Migrant templates
│       └── base.html       # Base template
│
├── requirements.txt        # Dependencies
├── run.py                  # Application entry point
└── .env                    # Environment variables
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Tamil Nadu Labour Welfare Department
- Flask and MongoDB communities

## Contact

For inquiries, please contact: info@migrantconnect-tn.gov.in

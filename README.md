# F1 API by RezRak

Welcome to the unofficial F1 API by RezRak! This API is updated for the 2023 season and provides various endpoints to retrieve information about races, drivers, and race results.

## Table of Contents

- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

### Prerequisites

- Python 3.11
- Flask
- SQLite3

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/RezRak/F1API.git
   cd F1API

2. Create a virtual environment and activate it:

    ```
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install the required packages:

   ```
   pip install -r requirements.txt

4. Create and initialize the database (Optional. You can use the provided database to keep 2023 stats. Running this will overwrite and create a new database):

   ```
   python3 createdatabase.py

5. Run the application:

   ```
   python3 app.py

## API Endpoints

Retrieve details for the specified season year.
```
GET /api/season/<year>
```

Add a new race to the specified season year. Authentication required.
```
POST /api/season/<year>/race
```

Add a new driver to the specified season year. Authentication required.
```
POST /api/season/<year>/drivers
```

Modify details of a specific race in the specified season year. Authentication required.
```
PUT /api/season/<year>/race/<race_name>
```

Modify details of a specific driver in the specified season year. Authentication required.
```
PUT /api/season/<year>/drivers/<driver_name>
```

Delete a specific race in the specified season year. Authentication required.
```
DELETE /api/season/<year>/race/<race_name>
```

Delete a specific driver in the specified season year. Authentication required.
```
DELETE /api/season/<year>/drivers/<driver_name>
```

Add race results for a specific race in the specified season year. Authentication required.
```
POST /api/season/<year>/race/int:race_id
```

Retrieve the points for all drivers after a specific race in the specified season year.
```
GET /api/season/<year>/points-after-race/int:race_id
```

## Authentication
The API uses Basic Authentication for endpoints that modify data. Use the following credentials or choose your own:

    Username: admin   
    Password: password





   





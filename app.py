from flask import Flask, jsonify, request
import sqlite3
from flask_basicauth import BasicAuth


app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'RezRak'
app.config['BASIC_AUTH_PASSWORD'] = '23pavilion'
basic_auth = BasicAuth()

database = 'F1Database.db'

def connect_db():
    return sqlite3.connect(database)

def query_db(query, args = (), one = False):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def modify_db(query, args = ()):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()


@app.route('/')
def home():
    # Use HTML tags for line breaks
    message = ('Welcome to an unofficial F1 API by RezRak<br>'
               'This API is updated for the 2023 season<br>'
               '<br>'
               'A list of available API calls:<br>'
               '<br>'
               'This will return all details for the specified season year: /api/season/<year>'
               '<br>'
               )

    return f"<html><body>{message}</body></html>"

@app.route('/api/season/<int:year>', methods = ['GET'])
def get_season(year):
    races = query_db('SELECT id, race_name, location, date, winner FROM races WHERE year = ?', [year])
    drivers = query_db('SELECT name, team, points FROM drivers WHERE year = ?',[year])

    if not races and not drivers:
        return jsonify({'Error: Season Not Found'}), 404

    return jsonify({
        "Races": [{"ID": r[0], "Race": r[1], "Location": r[2], "Date": r[3], "Winner": r[4]} for r in races],
        "Drivers": [{"Name": d[0], "Team": d[1], "Points": d[2]} for d in drivers]

    })

@app.route('/api/season/<int:year>/race', methods = ['POST'])
@basic_auth.required
def add_race(year):
    data = request.get_json()
    race_name = data['race_name']
    location = data['location']
    date = data['date']
    winner = data['winner']

    modify_db('INSERT INTO races (year, race_name, location, date, winner) VALUES (?, ?, ?, ?, ?)', [year, race_name, location, date, winner])
    return jsonify({"Message": year, race_name: " was successfully added!"}), 201

@app.route('/api/season/<int:year>/drivers', methods = ['POST'])
@basic_auth.required
def add_driver(year):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    name = data.get('name')
    team = data.get('team')
    points = data.get('points')

    if not name or not team or points is None:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        modify_db('INSERT INTO drivers (year, name, team, points) VALUES (?, ?, ?, ?)', [year, name, team, points])
        return jsonify({"message": "Driver added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/season/<int:year>/race/<race_name>', methods = ['PUT'])
@basic_auth.required
def modify_race(year, race_name):
    data = request.get_json()
    location = data['location']
    date = data['date']
    winner = data['winner']

    modify_db('UPDATE races SET location = ?, date = ?, winner = ? WHERE year = ? and race_name = ?', [location, date, winner, year, race_name])
    return jsonify({"Message: ", year, race_name + " was successfully updated"})

@app.route('/api/season/<int:year>/drivers/<driver_name>', methods = ['PUT'])
@basic_auth.required
def modify_drivers(year, driver_name):
    data = request.get_json()
    team = data['team']
    points = data['points']
    new_name = data.get('name')  # To handle name change if needed

    if new_name:
        modify_db('UPDATE drivers SET name = ?, team = ?, points = ? WHERE year = ? and name = ?', [new_name, team, points, year, driver_name])
        driver_name = new_name
    else:
        modify_db('UPDATE drivers SET team = ?, points = ? WHERE year = ? and name = ?', [team, points, year, driver_name])

    return jsonify({"message": f"{driver_name} was successfully updated for {year} season"})

@app.route('/api/season/<int:year>/race/<int:race_id>/results', methods = ['DELETE'])
@basic_auth.required
def delete_race_results(year, race_id):
    modify_db('DELETE FROM race_results WHERE race_id = ?', [race_id])
    return jsonify({"message": f"Results for race {race_id} in year {year} were successfully deleted"})

@app.route('/api/season/<int:year>/race/<int:race_id>', methods=['DELETE'])
@basic_auth.required
def delete_race(year, race_id):
    modify_db('DELETE FROM race_results WHERE race_id = ?', [race_id])
    modify_db('DELETE FROM races WHERE id = ?', [race_id])
    return jsonify({"message": f"Race with ID {race_id} was successfully deleted from {year} season"})


@app.route('/api/season/<int:year>/drivers/<driver_name>', methods = ['DELETE'])
@basic_auth.required
def delete_drivers(year, driver_name):
    #data = request.get_json()

    modify_db('DELETE FROM drivers WHERE year = ? AND name = ?', [year, driver_name])
    return jsonify({"message": f"{driver_name} was successfully deleted from {year} season"})

@app.route('/api/season/<int:year>/race/<int:race_id>', methods = ['POST'])
@basic_auth.required
def add_race_results(year, race_id):
    results = request.get_json().get('results', [])
    for result in results:
        driver_name = result['driver_name']
        points = result['points']

        driver = query_db('SELECT id FROM drivers WHERE name = ? AND year = ?', [driver_name, year], one=True)
        if driver:
            driver_id = driver[0]
            modify_db('INSERT INTO race_results (race_id, driver_id, points) VALUES (?, ?, ?)', [race_id, driver_id, points])
            modify_db('UPDATE drivers SET points = points + ? WHERE id = ?', [points, driver_id])
        else:
            return jsonify({"Driver not found for season": year}), 404

    return jsonify({"Message": "Race results were successfully added"}), 201


@app.route('/api/season/<int:year>/points-after-race/<int:race_id>', methods = ['GET'])
def get_points_after_race(year, race_id):

    drivers = query_db('SELECT id, name, team FROM drivers WHERE year = ?', [year])

    if not drivers:
        return jsonify({"Driver not found for ", year + " season"})

    driverPoints = {}

    for driver in drivers:
        driver_id, name, team = driver
        totalPoints = query_db('SELECT sum(points) FROM race_results where race_id <= ? AND driver_id = ?', [race_id, driver_id], one=True)[0]

        driverPoints[name] = {
            "team": team,
            "points": totalPoints if totalPoints else 0
        }

    return jsonify(driverPoints)

@app.route('/api/season/<int:year>/race-results/<int:race_id>', methods=['GET'])
def get_race_results(year, race_id):
    results = query_db('''
        SELECT d.name, r.points 
        FROM race_results r
        JOIN drivers d ON r.driver_id = d.id
        WHERE r.race_id = ? AND d.year = ?
    ''', [race_id, year])

    if not results:
        return jsonify({'Error: Race results not found'}), 404

    return jsonify({
        "Race ID": race_id,
        "Results": [{"Driver": r[0], "Points": r[1]} for r in results]
    })

if __name__ == '__main__':
    app.run(debug=True)











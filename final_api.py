from flask import Flask, jsonify, request
from datetime import datetime
import psycopg2

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect('postgresql://postgres:%40%23%24Py1009@localhost:5432/traffic_optimizer')

@app.route('/')
def root():
    return jsonify({'message': 'Smart Traffic Optimizer API', 'status': 'running'})

@app.route('/health')
def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'postgresql'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/traffic-data', methods=['POST'])
def add_traffic_data():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data or 'intersection_id' not in data or 'vehicle_count' not in data or 'avg_speed' not in data:
            return jsonify({'error': 'Missing required fields: intersection_id, vehicle_count, avg_speed'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO traffic_data (intersection_id, vehicle_count, avg_speed, queue_length, congestion_level, traffic_light_id)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id, timestamp
        ''', (
            data['intersection_id'], data['vehicle_count'], data['avg_speed'],
            data.get('queue_length', 0), data.get('congestion_level', 'medium'), 
            data.get('traffic_light_id', 'default_light')
        ))
        result = cursor.fetchone()
        conn.commit()
        return jsonify({'message': 'Data added', 'id': result[0], 'timestamp': result[1].isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/traffic-data', methods=['GET'])
def get_traffic_data():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, intersection_id, vehicle_count, avg_speed, queue_length, congestion_level, traffic_light_id, timestamp FROM traffic_data ORDER BY timestamp DESC LIMIT 50')
        data = []
        for row in cursor.fetchall():
            data.append({
                'id': row[0], 'intersection_id': row[1], 'vehicle_count': row[2], 
                'avg_speed': float(row[3]), 'queue_length': row[4], 'congestion_level': row[5],
                'traffic_light_id': row[6], 'timestamp': row[7].isoformat()
            })
        return jsonify({'count': len(data), 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/traffic-data/<intersection_id>', methods=['GET'])
def get_intersection_data(intersection_id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, intersection_id, vehicle_count, avg_speed, queue_length, congestion_level, traffic_light_id, timestamp FROM traffic_data WHERE intersection_id = %s ORDER BY timestamp DESC LIMIT 50', (intersection_id,))
        data = []
        for row in cursor.fetchall():
            data.append({
                'id': row[0], 'intersection_id': row[1], 'vehicle_count': row[2], 
                'avg_speed': float(row[3]), 'queue_length': row[4], 'congestion_level': row[5],
                'traffic_light_id': row[6], 'timestamp': row[7].isoformat()
            })
        return jsonify({'intersection_id': intersection_id, 'count': len(data), 'data': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/stats', methods=['GET'])
def get_stats():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*), AVG(vehicle_count), AVG(avg_speed) FROM traffic_data')
        result = cursor.fetchone()
        return jsonify({
            'total_records': result[0],
            'average_vehicles': float(result[1] or 0),
            'average_speed': float(result[2] or 0)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

@app.route('/test', methods=['GET'])
def test_system():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO traffic_data (intersection_id, vehicle_count, avg_speed) VALUES (%s, %s, %s) RETURNING id', ('test', 99, 50.5))
        test_id = cursor.fetchone()[0]
        conn.commit()
        return jsonify({'system': 'operational', 'test_id': test_id, 'message': 'Test successful'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == '__main__':
    print('?? Starting Final Smart Traffic Optimizer API')
    print('?? http://localhost:8000')
    app.run(host='0.0.0.0', port=8000, debug=False)

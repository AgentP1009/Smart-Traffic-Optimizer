from flask import Flask, jsonify, request
from datetime import datetime
import psycopg2
import sys
import os

# Add the correct paths - go up one level from api folder
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # This goes to main project folder

# Add the actual paths where modules are located
sys.path.append(project_root)  # Main project root
sys.path.append(os.path.join(project_root, '02_ai_vision', 'vision_engine'))
sys.path.append(os.path.join(project_root, '02_ai_vision', 'fusion_engine')) 
sys.path.append(os.path.join(project_root, '01_core_engine'))

print('Project root:', project_root)

try:
    from lightweight_detector import LightweightTrafficAnalyzer
    VISION_AVAILABLE = True
    print('✅ Vision module loaded successfully')
except ImportError as e:
    print('❌ Vision module not available:', e)
    VISION_AVAILABLE = False

try:
    from simple_fusion import SimpleFusionEngine
    FUSION_AVAILABLE = True
    print('✅ Fusion module loaded successfully')
except ImportError as e:
    print('❌ Fusion module not available:', e)
    FUSION_AVAILABLE = False

# Skip optimization engine for now to avoid import errors
OPTIMIZATION_AVAILABLE = False
print('⚠️ Optimization engine skipped (using fusion engine only)')

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
            return jsonify({'error': 'Missing required fields'}), 400

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

# VISION OPTIMIZATION ENDPOINT
@app.route('/api/vision-optimize', methods=['POST'])
def vision_optimize():
    '''Enhanced optimization using camera input'''
    if not VISION_AVAILABLE or not FUSION_AVAILABLE:
        return jsonify({'error': 'AI modules not available', 'status': 'failed'}), 500
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        intersection_id = data.get('intersection_id', 'default')
        
        # Get vision analysis
        vision_ai = LightweightTrafficAnalyzer()
        
        if data.get('image_url'):
            # Analyze from image file
            vision_data = vision_ai.analyze_traffic(data['image_url'])
        else:
            # Analyze from webcam
            vision_data = vision_ai.analyze_traffic()
        
        # Get existing traffic data
        existing_data = {'current_green_time': 30}
        
        # Fusion with existing system
        fusion = SimpleFusionEngine()
        optimization = fusion.fuse_data(vision_data, existing_data)
        
        return jsonify({
            'status': 'success',
            'intersection_id': intersection_id,
            'vision_analysis': vision_data,
            'optimization': optimization,
            'system': 'Lightweight AI Vision'
        })
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500

if __name__ == '__main__':
    print('Starting Smart Traffic Optimizer API with Vision')
    print('http://localhost:8000')
    app.run(host='0.0.0.0', port=8000, debug=False)

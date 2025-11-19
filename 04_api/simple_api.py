# SIMPLE WORKING API - NO COMPLEX IMPORTS
from flask import Flask, jsonify, request
from datetime import datetime
import psycopg2
import subprocess
import sys
import os

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect('postgresql://postgres:%40%23%24Py1009@localhost:5432/traffic_optimizer')

@app.route('/')
def root():
    return jsonify({'message': 'Smart Traffic Optimizer API', 'status': 'running'})

@app.route('/api/vision-optimize', methods=['POST'])
def vision_optimize():
    '''Simple vision optimization using external script'''
    try:
        data = request.get_json()
        intersection_id = data.get('intersection_id', 'default')
        
        # Run vision analysis as subprocess
        result = subprocess.run([
            sys.executable, '../07_tests/simple_traffic_vision.py'
        ], capture_output=True, text=True, cwd='..')
        
        if result.returncode == 0:
            # Parse the output (you'd need to modify simple_traffic_vision.py to return JSON)
            return jsonify({
                'status': 'success', 
                'intersection_id': intersection_id,
                'message': 'Vision analysis completed',
                'output': result.stdout
            })
        else:
            return jsonify({'error': result.stderr, 'status': 'failed'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500

if __name__ == '__main__':
    print('Starting Simple Traffic Optimizer API')
    print('http://localhost:8000')
    app.run(host='0.0.0.0', port=8000, debug=False)

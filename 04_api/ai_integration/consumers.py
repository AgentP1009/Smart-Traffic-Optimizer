import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class TrafficConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add(
            "traffic_updates",
            self.channel_name
        )
        await self.accept()
        
        # Send initial connection message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to Traffic Optimizer WebSocket'
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "traffic_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Handle different message types
        if data['type'] == 'detection_request':
            await self.handle_detection_request(data)
        elif data['type'] == 'subscribe_training':
            await self.subscribe_to_training(data)

    async def handle_detection_request(self, data):
        # Simulate real-time detection updates
        await self.send(text_data=json.dumps({
            'type': 'detection_progress',
            'progress': 25,
            'message': 'Processing image...'
        }))
        
        await self.send(text_data=json.dumps({
            'type': 'detection_progress', 
            'progress': 50,
            'message': 'Running YOLO model...'
        }))
        
        await self.send(text_data=json.dumps({
            'type': 'detection_progress',
            'progress': 75,
            'message': 'Analyzing results...'
        }))
        
        await self.send(text_data=json.dumps({
            'type': 'detection_complete',
            'vehicles_detected': 4,
            'detections': [
                {'vehicle': 'motorcycle', 'count': 2, 'confidence': 0.92},
                {'vehicle': 'car', 'count': 1, 'confidence': 0.87},
                {'vehicle': 'tuktuk', 'count': 1, 'confidence': 0.78}
            ]
        }))

    async def traffic_update(self, event):
        # Send traffic updates to all connected clients
        await self.send(text_data=json.dumps(event))

    async def training_progress(self, event):
        # Send training progress updates
        await self.send(text_data=json.dumps(event))
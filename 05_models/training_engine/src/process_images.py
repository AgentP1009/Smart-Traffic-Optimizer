"""
process_images_to_json.py
Converts labeled images to JSON format for training data
"""

import os
import json
import cv2
import glob
import numpy as np
from PIL import Image
import xml.etree.ElementTree as ET  # For XML labels (LabelImg format)
from datetime import datetime

class ImageProcessor:
    def __init__(self, image_folder, label_folder, output_json="dataset.json"):
        """
        Initialize processor
        
        Args:
            image_folder: Path to folder with images
            label_folder: Path to folder with label files
            output_json: Output JSON filename
        """
        self.image_folder = image_folder
        self.label_folder = label_folder
        self.output_json = output_json
        self.dataset_info = {
            "description": "Cambodia Traffic Detection Dataset",
            "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "classes": self.get_class_mapping(),
            "annotations": []
        }
        
        # Class mapping (adjust based on your labels)
        self.class_dict = {
            'moto': 0,
            'tuktuk': 1, 
            'bicycle': 2,
            'cart': 3,
            'car': 4,
            'truck': 5
        }
    
    def get_class_mapping(self):
        """Return class mapping dictionary"""
        return {
            "0": "moto",
            "1": "tuktuk", 
            "2": "bicycle",
            "3": "cart",
            "4": "car",
            "5": "truck"
        }
    
    def process_image(self, image_path):
        """
        Process a single image and extract metadata
        
        Returns:
            Dictionary with image info
        """
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                print(f"Warning: Cannot read image {image_path}")
                return None
            
            height, width, channels = img.shape
            
            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            
            # Get corresponding label file
            label_file = self.find_label_file(base_name)
            
            # Process based on label file format
            if label_file.endswith('.txt'):
                annotations = self.read_yolo_labels(label_file, width, height)
            elif label_file.endswith('.xml'):
                annotations = self.read_xml_labels(label_file)
            elif label_file.endswith('.json'):
                annotations = self.read_json_labels(label_file)
            else:
                print(f"No label file found for {base_name}")
                annotations = []
            
            # Create image info dictionary
            image_info = {
                "id": len(self.dataset_info["annotations"]) + 1,
                "filename": os.path.basename(image_path),
                "path": os.path.abspath(image_path),
                "width": width,
                "height": height,
                "channels": channels,
                "file_size": os.path.getsize(image_path),
                "objects": annotations
            }
            
            return image_info
            
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def find_label_file(self, base_name):
        """
        Find label file for given image
        
        Returns:
            Path to label file or empty string if not found
        """
        # Check for different label formats
        possible_extensions = ['.txt', '.xml', '.json']
        
        for ext in possible_extensions:
            label_path = os.path.join(self.label_folder, base_name + ext)
            if os.path.exists(label_path):
                return label_path
        
        # If not found, check with lowercase/uppercase variations
        for ext in possible_extensions:
            label_path = os.path.join(self.label_folder, base_name.lower() + ext)
            if os.path.exists(label_path):
                return label_path
        
        return ""
    
    def read_yolo_labels(self, label_path, img_width, img_height):
        """
        Read YOLO format labels (.txt files)
        
        YOLO format: class x_center y_center width height (normalized 0-1)
        """
        annotations = []
        
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    bbox_width = float(parts[3])
                    bbox_height = float(parts[4])
                    
                    # Convert YOLO format to pixel coordinates
                    x_min = (x_center - bbox_width/2) * img_width
                    y_min = (y_center - bbox_height/2) * img_height
                    x_max = (x_center + bbox_width/2) * img_width
                    y_max = (y_center + bbox_height/2) * img_height
                    
                    # Ensure coordinates are within image bounds
                    x_min = max(0, min(x_min, img_width))
                    y_min = max(0, min(y_min, img_height))
                    x_max = max(0, min(x_max, img_width))
                    y_max = max(0, min(y_max, img_height))
                    
                    annotation = {
                        "class_id": class_id,
                        "class_name": self.get_class_name(class_id),
                        "bbox": {
                            "x_min": float(x_min),
                            "y_min": float(y_min),
                            "x_max": float(x_max),
                            "y_max": float(y_max),
                            "width": float(x_max - x_min),
                            "height": float(y_max - y_min)
                        },
                        "area": float((x_max - x_min) * (y_max - y_min)),
                        "format": "yolo"
                    }
                    
                    annotations.append(annotation)
        
        except Exception as e:
            print(f"Error reading YOLO labels {label_path}: {e}")
        
        return annotations
    
    def read_xml_labels(self, label_path):
        """
        Read XML format labels (LabelImg format)
        """
        annotations = []
        
        try:
            tree = ET.parse(label_path)
            root = tree.getroot()
            
            # Get image size from XML
            size = root.find('size')
            img_width = int(size.find('width').text)
            img_height = int(size.find('height').text)
            
            # Read each object
            for obj in root.findall('object'):
                class_name = obj.find('name').text.lower()
                class_id = self.class_dict.get(class_name, -1)
                
                bbox = obj.find('bndbox')
                x_min = float(bbox.find('xmin').text)
                y_min = float(bbox.find('ymin').text)
                x_max = float(bbox.find('xmax').text)
                y_max = float(bbox.find('ymax').text)
                
                annotation = {
                    "class_id": class_id,
                    "class_name": class_name,
                    "bbox": {
                        "x_min": x_min,
                        "y_min": y_min,
                        "x_max": x_max,
                        "y_max": y_max,
                        "width": x_max - x_min,
                        "height": y_max - y_min
                    },
                    "area": float((x_max - x_min) * (y_max - y_min)),
                    "format": "xml"
                }
                
                annotations.append(annotation)
        
        except Exception as e:
            print(f"Error reading XML labels {label_path}: {e}")
        
        return annotations
    
    def read_json_labels(self, label_path):
        """
        Read JSON format labels
        """
        try:
            with open(label_path, 'r') as f:
                data = json.load(f)
            return data.get("annotations", [])
        except Exception as e:
            print(f"Error reading JSON labels {label_path}: {e}")
            return []
    
    def get_class_name(self, class_id):
        """Convert class ID to class name"""
        return self.dataset_info["classes"].get(str(class_id), f"unknown_{class_id}")
    
    def preprocess_images(self, output_folder="processed_images", target_size=(640, 640)):
        """
        Preprocess all images (resize, enhance, save)
        
        Returns:
            List of processed image paths
        """
        os.makedirs(output_folder, exist_ok=True)
        processed_images = []
        
        image_files = glob.glob(os.path.join(self.image_folder, "*.jpg")) + \
                      glob.glob(os.path.join(self.image_folder, "*.png")) + \
                      glob.glob(os.path.join(self.image_folder, "*.jpeg"))
        
        print(f"Found {len(image_files)} images to process")
        
        for img_path in image_files:
            try:
                # Read image
                img = cv2.imread(img_path)
                if img is None:
                    continue
                
                # Resize
                img_resized = cv2.resize(img, target_size)
                
                # Enhance based on conditions
                filename = os.path.basename(img_path).lower()
                
                if any(keyword in filename for keyword in ['night', 'dark', 'evening']):
                    # Brighten dark images
                    img_resized = cv2.convertScaleAbs(img_resized, alpha=1.3, beta=20)
                elif any(keyword in filename for keyword in ['rain', 'rainy', 'wet']):
                    # Enhance contrast for rainy images
                    img_resized = cv2.convertScaleAbs(img_resized, alpha=1.2, beta=10)
                
                # Save processed image
                output_path = os.path.join(output_folder, os.path.basename(img_path))
                cv2.imwrite(output_path, img_resized)
                processed_images.append(output_path)
                
                # Update the image path in dataset info
                print(f"Processed: {os.path.basename(img_path)}")
                
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
        
        return processed_images
    
    def process_all_images(self, preprocess=True):
        """
        Process all images and save to JSON
        
        Args:
            preprocess: Whether to preprocess images first
        """
        if preprocess:
            print("Preprocessing images...")
            self.preprocess_images()
            # Update image folder to processed images
            self.image_folder = "processed_images"
        
        print("Processing images to JSON format...")
        
        # Get all image files
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(self.image_folder, ext)))
        
        print(f"Found {len(image_files)} images")
        
        # Process each image
        for i, img_path in enumerate(image_files):
            if i % 10 == 0:
                print(f"Processing image {i+1}/{len(image_files)}...")
            
            image_info = self.process_image(img_path)
            if image_info:
                self.dataset_info["annotations"].append(image_info)
        
        # Add dataset statistics
        self.add_statistics()
        
        # Save to JSON file
        self.save_json()
        
        print(f"Processing complete! Saved to {self.output_json}")
    
    def add_statistics(self):
        """Add statistics to dataset info"""
        total_images = len(self.dataset_info["annotations"])
        total_objects = 0
        class_counts = {class_name: 0 for class_name in self.class_dict.keys()}
        
        for annotation in self.dataset_info["annotations"]:
            total_objects += len(annotation["objects"])
            for obj in annotation["objects"]:
                class_name = obj["class_name"]
                if class_name in class_counts:
                    class_counts[class_name] += 1
        
        self.dataset_info["statistics"] = {
            "total_images": total_images,
            "total_objects": total_objects,
            "average_objects_per_image": total_objects / total_images if total_images > 0 else 0,
            "class_distribution": class_counts
        }
    
    def save_json(self):
        """Save dataset info to JSON file"""
        with open(self.output_json, 'w', encoding='utf-8') as f:
            json.dump(self.dataset_info, f, indent=2, ensure_ascii=False)
    
    def export_for_yolo(self, output_folder="yolo_dataset"):
        """
        Export data in YOLO format for direct training
        
        Creates folder structure:
        yolo_dataset/
        ├── images/
        │   ├── train/
        │   └── val/
        └── labels/
            ├── train/
            └── val/
        """
        import shutil
        import random
        
        os.makedirs(os.path.join(output_folder, "images", "train"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "images", "val"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "labels", "train"), exist_ok=True)
        os.makedirs(os.path.join(output_folder, "labels", "val"), exist_ok=True)
        
        # Split data (80% train, 20% val)
        annotations = self.dataset_info["annotations"]
        random.shuffle(annotations)
        split_idx = int(0.8 * len(annotations))
        train_data = annotations[:split_idx]
        val_data = annotations[split_idx:]
        
        print(f"Train: {len(train_data)}, Val: {len(val_data)}")
        
        # Process train data
        for i, img_info in enumerate(train_data):
            # Copy image
            src_img = img_info["path"]
            dst_img = os.path.join(output_folder, "images", "train", img_info["filename"])
            shutil.copy2(src_img, dst_img)
            
            # Create YOLO labels
            label_file = os.path.splitext(img_info["filename"])[0] + ".txt"
            label_path = os.path.join(output_folder, "labels", "train", label_file)
            
            with open(label_path, 'w') as f:
                for obj in img_info["objects"]:
                    # Convert to YOLO format (normalized)
                    x_min = obj["bbox"]["x_min"]
                    y_min = obj["bbox"]["y_min"]
                    x_max = obj["bbox"]["x_max"]
                    y_max = obj["bbox"]["y_max"]
                    width = img_info["width"]
                    height = img_info["height"]
                    
                    x_center = ((x_min + x_max) / 2) / width
                    y_center = ((y_min + y_max) / 2) / height
                    bbox_width = (x_max - x_min) / width
                    bbox_height = (y_max - y_min) / height
                    
                    f.write(f"{obj['class_id']} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
        
        # Process validation data (same as above)
        for img_info in val_data:
            src_img = img_info["path"]
            dst_img = os.path.join(output_folder, "images", "val", img_info["filename"])
            shutil.copy2(src_img, dst_img)
            
            label_file = os.path.splitext(img_info["filename"])[0] + ".txt"
            label_path = os.path.join(output_folder, "labels", "val", label_file)
            
            with open(label_path, 'w') as f:
                for obj in img_info["objects"]:
                    x_min = obj["bbox"]["x_min"]
                    y_min = obj["bbox"]["y_min"]
                    x_max = obj["bbox"]["x_max"]
                    y_max = obj["bbox"]["y_max"]
                    width = img_info["width"]
                    height = img_info["height"]
                    
                    x_center = ((x_min + x_max) / 2) / width
                    y_center = ((y_min + y_max) / 2) / height
                    bbox_width = (x_max - x_min) / width
                    bbox_height = (y_max - y_min) / height
                    
                    f.write(f"{obj['class_id']} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")
        
        # Create data.yaml for YOLO
        yaml_content = f"""path: {os.path.abspath(output_folder)}
train: images/train
val: images/val

nc: {len(self.class_dict)}
names: {list(self.class_dict.keys())}
"""
        
        with open(os.path.join(output_folder, "data.yaml"), 'w') as f:
            f.write(yaml_content)
        
        print(f"YOLO dataset exported to {output_folder}/")
        print(f"data.yaml created. You can now train with: yolo train data={output_folder}/data.yaml")


# ==================== USAGE EXAMPLES ====================

# Example 1: Basic processing to JSON
def example_basic():
    processor = ImageProcessor(
        image_folder="raw_images",
        label_folder="labels",
        output_json="cambodia_traffic_dataset.json"
    )
    processor.process_all_images(preprocess=True)

# Example 2: Process and export for YOLO
def example_yolo_export():
    processor = ImageProcessor(
        image_folder="raw_images",
        label_folder="labels",
        output_json="dataset.json"
    )
    processor.process_all_images(preprocess=True)
    processor.export_for_yolo(output_folder="yolo_ready_dataset")

# Example 3: Read and analyze existing JSON
def analyze_json(json_file="dataset.json"):
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Dataset: {data['description']}")
    print(f"Created: {data['created']}")
    print(f"Total images: {data['statistics']['total_images']}")
    print(f"Total objects: {data['statistics']['total_objects']}")
    
    print("\nClass distribution:")
    for class_name, count in data['statistics']['class_distribution'].items():
        print(f"  {class_name}: {count}")
    
    # Show first image info as example
    if data['annotations']:
        first_img = data['annotations'][0]
        print(f"\nFirst image: {first_img['filename']}")
        print(f"Objects detected: {len(first_img['objects'])}")
        for obj in first_img['objects']:
            print(f"  - {obj['class_name']} at [{obj['bbox']['x_min']:.0f}, {obj['bbox']['y_min']:.0f}]")

# Example 4: Simple one-line processing
def quick_process():
    ImageProcessor("images", "labels").process_all_images()

if __name__ == "__main__":
    print("Cambodia Traffic Image Processor")
    print("=" * 40)
    
    # Run basic example
    example_basic()
    
    # Optional: Export for YOLO
    # example_yolo_export()
    
    # Optional: Analyze the created JSON
    # analyze_json("cambodia_traffic_dataset.json")
import cv2
import numpy as np
import onnxruntime as ort
import json
import time # For optional absolute timestamp

# Path to your exported ONNX model
model_path = "yolo11n.onnx"
# Class names (adjust this based on your dataset, COCO has 80 classes)
CLASS_NAMES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck",
    "boat", "traffic light", "fire hydrant", "stop sign", "parking meter", "bench",
    "bird", "cat", "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra",
    "giraffe", "backpack", "umbrella", "handbag", "tie", "suitcase", "frisbee",
    "skis", "snowboard", "sports ball", "kite", "baseball bat", "baseball glove",
    "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange",
    "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair", "couch",
    "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]

# Confidence threshold and NMS threshold
CONF_THRESHOLD = 0.25
NMS_THRESHOLD = 0.45

# Input size (must match the imgsz used during ONNX export)
INPUT_WIDTH = 640
INPUT_HEIGHT = 640

# Create an ONNX Runtime session
try:
    session = ort.InferenceSession(model_path, providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    print("Using ONNX Runtime with CUDA (if available), otherwise CPU.")
except Exception as e:
    print(f"Error initializing ONNX Runtime session with CUDA: {e}. Falling back to CPU only.")
    session = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])

# Get input and output names from the ONNX model
input_name = session.get_inputs()[0].name
output_names = [output.name for output in session.get_outputs()]

print(f"Model Input Name: {input_name}")
print(f"Model Output Names: {output_names}")

# Open camera
cap = cv2.VideoCapture(0) # 0 for default webcam. Change to video file path if needed.

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_count = 0

print("Starting object detection. Press Ctrl+C to stop.")

try: # Use a try-except block to gracefully handle Ctrl+C
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame. Exiting.")
            break

        frame_count += 1

        # Preprocessing
        resized_frame = cv2.resize(frame, (INPUT_WIDTH, INPUT_HEIGHT))
        rgb_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        input_tensor = rgb_frame.astype(np.float32) / 255.0
        input_tensor = np.transpose(input_tensor, (2, 0, 1))
        input_tensor = np.expand_dims(input_tensor, axis=0)

        # Run inference with ONNX Runtime
        outputs = session.run(output_names, {input_name: input_tensor})

        predictions = outputs[0]
        if predictions.ndim == 3 and predictions.shape[1] == (len(CLASS_NAMES) + 4):
            predictions = predictions.transpose(0, 2, 1)

        boxes = []
        confidences = []
        class_ids = []

        x_factor = frame.shape[1] / INPUT_WIDTH
        y_factor = frame.shape[0] / INPUT_HEIGHT

        for detection in predictions[0]:
            scores = detection[4:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > CONF_THRESHOLD:
                center_x = int(detection[0] * x_factor)
                center_y = int(detection[1] * y_factor)
                width = int(detection[2] * x_factor)
                height = int(detection[3] * y_factor)

                x = int(center_x - width / 2)
                y = int(center_y - height / 2)

                boxes.append([x, y, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, CONF_THRESHOLD, NMS_THRESHOLD)

        detections_for_json = []

        if len(indices) > 0:
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                label = str(CLASS_NAMES[class_ids[i]])
                confidence = confidences[i]

                detections_for_json.append({
                    "class_name": label,
                    "confidence": round(confidence, 4),
                    "bounding_box": {
                        "x": x,
                        "y": y,
                        "width": w,
                        "height": h
                    }
                })

        frame_data = {
            "frame_id": frame_count,
            "timestamp_relative_sec": cv2.getTickCount() / cv2.getTickFrequency(),
            "timestamp_absolute_iso": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time())), # Optional: absolute timestamp
            "detections": detections_for_json
        }

        # Convert the dictionary to a JSON string and print it
        print(json.dumps(frame_data, indent=2))

        # You might want to introduce a small delay if the console output is too fast
        # time.sleep(0.1) # Example: wait 100ms between frames

except KeyboardInterrupt:
    print("\nDetection stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    cap.release()
    # No need for cv2.destroyAllWindows() as no windows were created
    print("Camera released. Exiting program.")
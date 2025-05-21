import cv2
import numpy as np
import onnxruntime as ort
import json # Import the json library

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
CONF_THRESHOLD = 0.25 # Objects with confidence below this are discarded
NMS_THRESHOLD = 0.45  # IoU threshold for Non-Maximum Suppression

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
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

frame_count = 0 # To keep track of frames

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    # You might want to print JSON for every N frames to avoid console spam
    # For now, we'll print for every frame, but consider uncommenting the line below
    # if frame_count % 5 == 0: # Example: print every 5th frame

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

    # --- Prepare data for JSON output ---
    detections_for_json = []

    if len(indices) > 0:
        for i in indices.flatten():
            x, y, w, h = boxes[i]
            label = str(CLASS_NAMES[class_ids[i]])
            confidence = confidences[i]

            # Add detection details to our list
            detections_for_json.append({
                "class_name": label,
                "confidence": round(confidence, 4), # Round for cleaner output
                "bounding_box": {
                    "x": x,
                    "y": y,
                    "width": w,
                    "height": h
                }
            })

            # Draw on frame (for visualization)
            color = (0, 255, 0) # Green bounding box
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # --- Print JSON output for the current frame ---
    frame_data = {
        "frame_id": frame_count,
        "timestamp": cv2.getTickCount() / cv2.getTickFrequency(), # More accurate timestamp
        "detections": detections_for_json
    }

    # Convert the dictionary to a JSON string and print it
    print(json.dumps(frame_data, indent=2)) # indent=2 makes it pretty-printed

    # Display the result
    cv2.imshow("YOLOv11 Object Detection (ONNX Runtime)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
import os
from ultralytics import YOLO
import cv2

# Using a standard YOLOv8 model for object detection
model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'yolov8n.pt')
model = YOLO(model_dir)
# Names of classes
names = model.names


class ObjectDetection:
    """
    Class for detecting objects in photos and videos using the YOLOv8n pre-trained model
    """

    # Instance of singleton class
    __instance = None

    def __new__(cls):
        """
        For Singleton design pattern
        """

        if cls.__instance is None:
            cls.__instance = super(ObjectDetection, cls).__new__(cls)
        return cls.__instance

    def __init__(self):
        pass

    def detect_objects_photo(self, photo_path: str) -> str:
        """
        Detects objects in an image
        :param photo_path: photo to find objects in
        :return: string with detected objects and confidence levels on their own lines
        """

        # Read image
        image = cv2.imread(photo_path)

        # Perform object detection on photo and get result
        result = model.predict(image, imgsz=1280, conf=0.4)[0]

        # Holds output string
        output = ''

        # For each box get the object class and confidence
        for box in result.boxes:
            object_name = names[int(box.cls)]
            conf_percentage = "{:.0%}".format(float(box.conf))
            output += f"{object_name} - confidence {conf_percentage} \n"

        return output

    @staticmethod
    def detect_objects_video(video_path: str) -> str:
        """
        Detects objects in a video
        :param video_path: path to the video file
        :return: string with detected objects and confidence levels on their own lines
        """

        # Open the video file
        cap = cv2.VideoCapture(video_path)

        # Will store results from the detection
        all_results = []
        ret = True

        # Loop through each frame of the video
        while ret:
            # Read a frame from the video
            ret, frame = cap.read()
            # If frame reading successful then detect and track objects in frame
            if ret:
                # Detect and track objects
                results = model.track(frame, persist=True, imgsz=640, conf=0.5)
                all_results.append(results)

        # List of tuples (id, object name, confidence level)
        inc_tuples = []
        # Iterate through results from object detection across video frames
        for results in all_results:
            result = results[0]
            # Iterate through each detection box in the frame
            for box in result.boxes:
                # Check if box.id is not None
                if box.id is not None:
                    # Format a string output for classes of object found and confidence
                    object_name = names[int(box.cls)]
                    object_tuple = (int(box.id), object_name, float(box.conf))
                    inc_tuples.append(object_tuple)

        # Accumulating confidence scores
        accumulated_scores = {}

        # Iterate through inc_tuples to accumulate confidence scores
        for object_tuple in inc_tuples:
            id_, object_name, conf_score = object_tuple
            key = (id_, object_name)
            if key in accumulated_scores:
                accumulated_scores[key].append(conf_score)
            else:
                accumulated_scores[key] = [conf_score]

        # Create a new list of tuples with (id, object name, average confidence score)
        new_inc_tuples = []
        for key, conf_scores in accumulated_scores.items():
            id_, object_name = key
            avg_conf_score = sum(conf_scores) / len(conf_scores)
            new_inc_tuples.append((id_, object_name, avg_conf_score))

        # Create string of objects and confidences
        output = ""
        for obj_tuple in new_inc_tuples:
            id_, object_name, avg_confidence = obj_tuple
            output += f"{object_name} - average confidence {avg_confidence:.0%}\n"

        return output

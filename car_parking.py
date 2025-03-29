import json
import cv2
import pickle
import cvzone
import numpy as np
from probability import calculate_probability 


with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


def load_database():
    with open("database.json", "r") as file:
        return json.load(file)


def save_database(data):
    with open("database.json", "w") as file:
        json.dump(data, file, indent=4)


def checkParkingSpace(imgPro):
    data = load_database()
    free_spaces = 0

    for pos in posList:
        x, y = pos
        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900: 
            color = (0, 255, 0)
            thickness = 5
            free_spaces += 1
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=1,
                           thickness=2, offset=0, colorR=color)


    if free_spaces != data["parking_lot"]["free_spaces"]:
        data["parking_lot"]["free_spaces"] = free_spaces
        data["parking_lot"]["occupied_spaces"] = data["parking_lot"]["total_spaces"] - free_spaces
        save_database(data)

    return data["parking_lot"]

cap = cv2.VideoCapture('C:\\Users\\Asus\\OneDrive\\Desktop\\all\\DATA SCIENCE AND ML\\PATHWAY\\projects\\car parking\\carPark.mp4')

while True:
    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    success, img = cap.read()
    if not success:
        break 

    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    parking_data = checkParkingSpace(imgDilate)  
    probability = calculate_probability()  

    print(f"Total Spaces: {parking_data['total_spaces']}, Free: {parking_data['free_spaces']}, "
          f"Occupied: {parking_data['occupied_spaces']}, Probability: {probability}%")

    cv2.imshow("Image", img)
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break  

cap.release() 
cv2.destroyAllWindows()

from nao_ip import NAO_IP
from naoqi import ALProxy
import numpy as np
import pandas as pd
import cv2
import os
import time


def camera_angle_to_pixel(coord, width, height):
    x = - int(coord[0]*width) + width//2
    y = int(coord[1]*width) + height//2
    return x, y


def store_face_info(videoDevice_proxy, faceDetection_proxy, memory_proxy,
                    only_first_face=False,
                    only_first_face_id=True,
                    videoDevice_args={"resolution": 2, "colorSpace": 11, "fps": 30},
                    faceDetection_args={"tims_ms": 500},
                    memory_args={"mem_value": "FaceDetected"}, 
                    image_args={"width": 248, "height": 248, "margin": 10},
                    file_args={"unknown_person_dir": "data\\people\\unknown\\"}):
    """Stores the faces detected by the robot"""

    assert not(only_first_face_id and only_first_face), "only_first_face must be False if only_first_face_id is True"

    # if the folder already exists, add a suffix to the folder and create a new one
    i = 1
    while os.path.exists(file_args["unknown_person_dir"]):
        file_args["unknown_person_dir"] = "data\\people\\unknown_" + str(i) + "\\"
        i += 1
    os.makedirs(file_args["unknown_person_dir"])

    # Register a Generic Video Module
    nameId = videoDevice_proxy.subscribeCamera("camera_sfi", 0, videoDevice_args["resolution"], videoDevice_args["colorSpace"], videoDevice_args["fps"])

    # Subscribe to the face detection
    faceDetection_proxy.subscribe("FaceDetection", faceDetection_args["tims_ms"], 0.0)

    # Create an image
    image = videoDevice_proxy.getImageRemote(nameId)

    # create the empty dataframe
    face_info_df = pd.DataFrame(columns=["timeStamp", "faceID", "scoreReco", "faceLabel", "shapeInfo_alpha", "shapeInfo_beta", "shapeInfo_width", "shapeInfo_height",
                                        "leftEye_center_x", "leftEye_center_y", "leftEye_nose_limit_x", "leftEye_nose_limit_y", "leftEye_ear_limit_x", "leftEye_ear_limit_y",
                                        "rightEye_center_x", "rightEye_center_y", "rightEye_nose_limit_x", "rightEye_nose_limit_y", "rightEye_ear_limit_x", "rightEye_ear_limit_y",
                                        "nose_center_x", "nose_center_y", "nose_left_limit_x", "nose_left_limit_y", "nose_right_limit_x", "nose_right_limit_y",
                                        "mouth_left_limit_x", "mouth_left_limit_y", "mouth_right_limit_x", "mouth_right_limit_y", "mouth_top_limit_x", "mouth_top_limit_y"])

    runnning = True

    while runnning:
        try:
            image = videoDevice_proxy.getImageRemote(nameId)
            imageWidth = image[0]
            imageHeight = image[1]
            array = image[6]
            img = np.frombuffer(array, dtype=np.uint8).reshape(imageHeight, imageWidth, 3).copy()
            val = memory_proxy.getData(memory_args["mem_value"])

            if val and len(val) > 0:
                # timeStamp = val[0]
                # faceInfoArray = val[1]
                # shapeInfo = faceInfoArray[0][0] # [0, alpha, beta, width, height]
                # extraInfo = faceInfoArray[0][1]
                # faceID = extraInfo[0]           # face ID
                # scoreReco = extraInfo[1]        # score
                # faceLabel = extraInfo[2]        # label
                # leftEyePoints = extraInfo[3]    # [center_x, center_y, nose_limit_x, nose_limit_y, ear_limit_x, ear_limit_y, 0, 0, 0, 0, 0, 0, 0, 0]
                # rightEyePoints = extraInfo[4]   # [center_x, center_y, nose_limit_x, nose_limit_y, ear_limit_x, ear_limit_y, 0, 0, 0, 0, 0, 0, 0, 0]
                # nosePoints = extraInfo[-2]      # [center_x, center_y, left_limit_x, left_limit_y, right_limit_x, right_limit_y]
                # mouthPoints = extraInfo[-1]     # [left_limit_x, left_limit_y, right_limit_x, right_limit_y, top_limit_x, top_limit_y, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

                # add the face info to the dataframe from val
                face_info_df = face_info_df.append({
                    "timeStamp": str(val[0]), "faceID": val[1][0][1][0], "scoreReco": val[1][0][1][1], "faceLabel": val[1][0][1][2], "shapeInfo_alpha": val[1][0][0][1], "shapeInfo_beta": val[1][0][0][2], "shapeInfo_width": val[1][0][0][3], "shapeInfo_height": val[1][0][0][4],
                    "leftEye_center_x": val[1][0][1][3][0], "leftEye_center_y": val[1][0][1][3][1], "leftEye_nose_limit_x": val[1][0][1][3][2], "leftEye_nose_limit_y": val[1][0][1][3][3], "leftEye_ear_limit_x": val[1][0][1][3][4], "leftEye_ear_limit_y": val[1][0][1][3][5],
                    "rightEye_center_x": val[1][0][1][4][0], "rightEye_center_y": val[1][0][1][4][1], "rightEye_nose_limit_x": val[1][0][1][4][2], "rightEye_nose_limit_y": val[1][0][1][4][3], "rightEye_ear_limit_x": val[1][0][1][4][4], "rightEye_ear_limit_y": val[1][0][1][4][5],
                    "nose_center_x": val[1][0][1][-2][0], "nose_center_y": val[1][0][1][-2][1], "nose_left_limit_x": val[1][0][1][-2][2], "nose_left_limit_y": val[1][0][1][-2][3], "nose_right_limit_x": val[1][0][1][-2][4], "nose_right_limit_y": val[1][0][1][-2][5],
                    "mouth_left_limit_x": val[1][0][1][-1][0], "mouth_left_limit_y": val[1][0][1][-1][1], "mouth_right_limit_x": val[1][0][1][-1][2], "mouth_right_limit_y": val[1][0][1][-1][3], "mouth_top_limit_x": val[1][0][1][-1][4], "mouth_top_limit_y": val[1][0][1][-1][5]
                }, ignore_index=True)
                
                # Draw the face rectangle
                max_shape_dim = max(face_info_df["shapeInfo_width"].iloc[-1], face_info_df["shapeInfo_height"].iloc[-1])
                alpha = face_info_df["shapeInfo_alpha"].iloc[-1]
                beta = face_info_df["shapeInfo_beta"].iloc[-1]
                face_coord1 = camera_angle_to_pixel((alpha - max_shape_dim/2.0, beta - max_shape_dim/2.0), imageWidth, imageHeight)
                face_coord2 = camera_angle_to_pixel((alpha + max_shape_dim/2.0, beta + max_shape_dim/2.0), imageWidth, imageHeight)

                # crop the image
                margin = image_args["margin"]
                face_img = img[face_coord1[1]-margin:face_coord2[1]+margin, face_coord2[0]-margin:face_coord1[0]+margin]

                # resahpe the image to width x height
                face_img = cv2.resize(face_img, (image_args["width"], image_args["height"]))

                # save the image to the unknown folder
                timeStamp = val[0]
                cv2.imwrite(file_args["unknown_person_dir"] + "face_" + str(timeStamp[0]) + "_" + str(timeStamp[1]) + ".jpg", face_img)

                if only_first_face:
                    runnning = False
                
                if only_first_face_id and len(face_info_df) > 1 and face_info_df["faceID"].iloc[-1] != face_info_df["faceID"].iloc[-2]:
                    runnning = False
                
                time.sleep(0.2)
            
        except KeyboardInterrupt:
            runnning = False
        
    # remove identical rows
    face_info_df = face_info_df.drop_duplicates(subset=["timeStamp"])
    
    # save the dataframe to a csv file
    face_info_df.to_csv(file_args["unknown_person_dir"] + "face_info.csv", index=False)
    
    videoDevice_proxy.unsubscribe(nameId)
    faceDetection_proxy.unsubscribe("FaceDetection")


if __name__ == "__main__":
    # create the proxies
    videoDevice = ALProxy("ALVideoDevice", NAO_IP, 9559)
    faceDetection = ALProxy("ALFaceDetection", NAO_IP, 9559)
    memory = ALProxy("ALMemory", NAO_IP, 9559)

    # store the face info
    store_face_info(videoDevice, faceDetection, memory)
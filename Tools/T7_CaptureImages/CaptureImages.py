from naoqi import ALProxy
import numpy as np
import pandas as pd
import cv2
import os
import time
import logging

class CaptureImages:
    """Capture images from the robot and store them in a folder"""

#%% CONSTRUCTOR ===========================================================================================================
    
    def __init__(self, output_image_folder, nao_ip, video_device_args, face_detection_time_ms, image_args, interval, number_of_images):
        self.__image_folder = output_image_folder
        self.__nao_ip = nao_ip
        self.__video_device_args = video_device_args
        self.__face_detection_time_ms = face_detection_time_ms
        self.__image_args = image_args
        self.__delay = interval
        self.__keep_n_images = number_of_images

        self.__video_device_proxy = ALProxy("ALVideoDevice", self.__nao_ip, 9559)
        self.__face_detection_proxy = ALProxy("ALFaceDetection", self.__nao_ip, 9559)
        self.__memory_proxy = ALProxy("ALMemory", self.__nao_ip, 9559)

        self.__face_info_df = None
        self.__name_id = None
        self.__runnning = False

#%% METHODS ==============================================================================================================

    def __read_df(self):
        """Read the face info dataframe from the csv file"""
        # check if the file exists
        if not os.path.exists(self.__image_folder + "face_info.csv"):
            return pd.DataFrame(columns=[
                    "timeStamp", "faceID", "scoreReco", "faceLabel", "shapeInfo_alpha", "shapeInfo_beta", "shapeInfo_width", "shapeInfo_height",
                    "leftEye_center_x", "leftEye_center_y", "leftEye_nose_limit_x", "leftEye_nose_limit_y", "leftEye_ear_limit_x", "leftEye_ear_limit_y",
                    "rightEye_center_x", "rightEye_center_y", "rightEye_nose_limit_x", "rightEye_nose_limit_y", "rightEye_ear_limit_x", "rightEye_ear_limit_y",
                    "nose_center_x", "nose_center_y", "nose_left_limit_x", "nose_left_limit_y", "nose_right_limit_x", "nose_right_limit_y",
                    "mouth_left_limit_x", "mouth_left_limit_y", "mouth_right_limit_x", "mouth_right_limit_y", "mouth_top_limit_x", "mouth_top_limit_y"])
        return pd.read_csv(self.__image_folder + "face_info.csv")
    
    def __write_df(self):
        self.__face_info_df.to_csv(self.__image_folder + "face_info.csv", index=False)
    
    def __delete_oldest_image_if_needed(self):
        """Delete the oldest image if the number of images is greater than the limit"""
        images = os.listdir(self.__image_folder)
        if len(images) > self.__keep_n_images:
            oldest_image = min(images)
            os.remove(self.__image_folder + oldest_image)
            # also remove the corresponding row from the dataframe
            self.__face_info_df = self.__face_info_df[self.__face_info_df["timeStamp"] != oldest_image[:-4]]
        
    def __write_image(self, image, time_stamp):
        cv2.imwrite(self.__image_folder + time_stamp + ".jpg", image)

#%% GETTERS AND SETTERS ==================================================================================================

    def get_face_info_df(self):
        return self.__face_info_df
    
    def get_running(self):
        return self.__runnning
    
    def get_image_folder(self):
        return self.__image_folder
    
    def set_image_folder(self, image_folder):
        self.__image_folder = image_folder
    
    def get_interval(self):
        return self.__delay
    
    def set_interval(self, interval):
        self.__delay = interval

#%% START AND STOP =======================================================================================================

    def start(self):
        self.__runnning = True
        self.__name_id = self.__video_device_proxy.subscribeCamera("camera_sfi", 0, self.__video_device_args["resolution"], self.__video_device_args["color_space"], self.__video_device_args["fps"])
        self.__face_detection_proxy.subscribe("FaceDetection", self.__face_detection_time_ms, 0.0)

        self.__face_info_df = self.__read_df()
        
        while self.__runnning:
            try:
                image_remote = self.__video_device_proxy.getImageRemote(self.__name_id)
                image_width = image_remote[0]
                image_height = image_remote[1]
                array = image_remote[6]
                image = np.frombuffer(array, dtype=np.uint8).reshape(image_height, image_width, 3).copy()

                time_stamp = str(time.time())

                face_detected = self.__memory_proxy.getData("FaceDetected", 0)

                if face_detected and len(face_detected) > 2:
                    # timeStamp = face_detected[0]
                    # faceInfoArray = face_detected[1]
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
                    self.__face_info_df = self.__face_info_df.append({
                        "timeStamp": time_stamp, "faceID": face_detected[1][0][1][0], "scoreReco": face_detected[1][0][1][1], "faceLabel": face_detected[1][0][1][2], "shapeInfo_alpha": face_detected[1][0][0][1], "shapeInfo_beta": face_detected[1][0][0][2], "shapeInfo_width": face_detected[1][0][0][3], "shapeInfo_height": face_detected[1][0][0][4],
                        "leftEye_center_x": face_detected[1][0][1][3][0], "leftEye_center_y": face_detected[1][0][1][3][1], "leftEye_nose_limit_x": face_detected[1][0][1][3][2], "leftEye_nose_limit_y": face_detected[1][0][1][3][3], "leftEye_ear_limit_x": face_detected[1][0][1][3][4], "leftEye_ear_limit_y": face_detected[1][0][1][3][5],
                        "rightEye_center_x": face_detected[1][0][1][4][0], "rightEye_center_y": face_detected[1][0][1][4][1], "rightEye_nose_limit_x": face_detected[1][0][1][4][2], "rightEye_nose_limit_y": face_detected[1][0][1][4][3], "rightEye_ear_limit_x": face_detected[1][0][1][4][4], "rightEye_ear_limit_y": face_detected[1][0][1][4][5],
                        "nose_center_x": face_detected[1][0][1][-2][0], "nose_center_y": face_detected[1][0][1][-2][1], "nose_left_limit_x": face_detected[1][0][1][-2][2], "nose_left_limit_y": face_detected[1][0][1][-2][3], "nose_right_limit_x": face_detected[1][0][1][-2][4], "nose_right_limit_y": face_detected[1][0][1][-2][5],
                        "mouth_left_limit_x": face_detected[1][0][1][-1][0], "mouth_left_limit_y": face_detected[1][0][1][-1][1], "mouth_right_limit_x": face_detected[1][0][1][-1][2], "mouth_right_limit_y": face_detected[1][0][1][-1][3], "mouth_top_limit_x": face_detected[1][0][1][-1][4], "mouth_top_limit_y": face_detected[1][0][1][-1][5]
                    }, ignore_index=True)
                
                self.__write_image(image, time_stamp)
                self.__delete_oldest_image_if_needed()
                self.__write_df()

                time.sleep(self.__delay)

            except Exception as e:
                logging.error("CaptureImages: " + str(e))
        
        logging.info("CaptureImages: Finished.")
    
    def stop(self):
        self.__runnning = False
        if self.__name_id:
            try:
                self.__video_device_proxy.unsubscribe(self.__name_id)
                self.__face_detection_proxy.unsubscribe("FaceDetection")
            except Exception as e:
                logging.error("CaptureImages: unsubscribing error: " + str(e))
        
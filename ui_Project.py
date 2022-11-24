import cv2
import face_recognition
import numpy as np

def get_face_infos(image):
    # Find all face
    face_location = face_recognition.face_locations(np.array(image), number_of_times_to_upsample=2)[0]

    # Now I am going to encode the face that I have detected
    encode_image = face_recognition.face_encodings(image)[0]
    top_pos, right_pos, bottom_pos, left_pos = face_location
    cv2.rectangle(image, (right_pos, bottom_pos), (left_pos, top_pos), (0, 255, 255), 2)
    return_tuple = (face_location, encode_image, image)

    return return_tuple
# get_face_infos

#!/usr/bin/python3
import os
import cv2
import dlib
import numpy
import pickle
import face_recognition
from datetime import datetime
from collections import Counter
from PIL import Image, UnidentifiedImageError

def train_new_face(datapath):
    amt_of_imgs = 20 # 20 images should be enough to establish an initial dataset
    new_name = input("Enter name of person to be trained: ")
    new_folder = f"{datapath}/training/{new_name}"
    if os.path.isdir(new_folder):
        print("Error: User already exists. Try a different name")
        exit()
    else:
        os.mkdir(new_folder)
        print("Created path:", new_folder)
        
        input(f"Ensure that only {new_name} is in view of the webcam. Press enter when ready.")
        good_pics = 0
        while good_pics < amt_of_imgs:
                result, orig_png = cv2.VideoCapture(0).read()
                if result:
                    png = numpy.asarray(orig_png)
                    png = cv2.cvtColor(png, cv2.COLOR_BGR2RGB)
                    try:
                        face_recognition.face_encodings(png)[0]
                        save_path = f"{new_folder}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
                        cv2.imwrite(save_path, orig_png)
                        print(int((good_pics + 1 / amt_of_imgs) * 100), "%\tWrote image to", save_path)
                        good_pics += 1
                    except IndexError:
                        print("Could not find face. Trying again.")
                else:
                    print("Error taking photo. Exiting.")
                    exit()
        print("Input data gathered. Run ./Robot.py to encode data.")
        #print("Photos complete. Now encoding data.")

def encode_known_faces(datapath, enc_path, model="hog"):
    # Append to already existing encoding file if possible
    if not os.path.isfile(enc_path):
        dataset = { "names" : [], "encodings" : [], "filepaths" : [] }
    else:
        with open(enc_path, "rb") as pickle_file:
            dataset = pickle.load(pickle_file)

    # Loop over all folders in training data
    for person in os.listdir(f"{datapath}/training"):
        for index, image in enumerate(os.listdir(f"{datapath}/training/{person}")):
            filepath = f"{datapath}/training/{person}/{image}"
            if filepath in dataset["filepaths"]:
                pass
                # print("Skipping duplicate filename:", filepath)
            elif "unknown_" in filepath:
                pass
                # print("Skipping unrecognizable face:", filepath)
            else:
                try:
                    img_data = Image.open(filepath)
                    img_data = numpy.asarray(img_data)
                    img_data = cv2.cvtColor(img_data, cv2.COLOR_BGR2RGB)
                    # locations = face_recognition.face_locations(img_data, model=model)
                    face_encoding = face_recognition.face_encodings(img_data)[0] # Limit one face per pic.

                    dataset["names"].append(person)
                    dataset["encodings"].append(face_encoding)
                    dataset["filepaths"].append(filepath)

                    progress = index + 1 / len(list(filter(lambda f : "unknown_" not in f, os.listdir(f'{datapath}/training/{person}')))) * 100
                    # print(int(progress), "%\tConverted:", filepath)
                except TypeError as e:
                    pass
                    print("Error: Could not encode Image:", filepath, "\n", str(e))
                except UnidentifiedImageError:
                    print("Error: Unrecognized file type:", filepath)
                except IndexError as e:
                    print("Error: Could not find face in Image:", filepath)
                    os.rename(filepath, f"{datapath}/training/{person}/unknown_{image}")

    with open(enc_path, "wb") as pickle_file: 
        pickle.dump(dataset, pickle_file)

def recognize_face(datapath, enc_path, model="hog"):

    # Ensure encoding is up to date
    encode_known_faces(datapath, enc_path, model) 

    # Take and save picture
    camera_port = 0 # Initial picture
    camera = cv2.VideoCapture(camera_port)
    result, orig_png = camera.read()
    if result:
        png = numpy.asarray(orig_png)
        png = cv2.cvtColor(png, cv2.COLOR_BGR2RGB)
        
        # Encode unknown face
        try:
            unknown_encoding = face_recognition.face_encodings(png)[0]
        except IndexError:
            return "unknown user"

        # Determine face based on encodings
        with open(enc_path, "rb") as pickle_file:
            dataset = pickle.load(pickle_file)
        boolean_matches = face_recognition.compare_faces(dataset["encodings"], unknown_encoding)
        votes = Counter(name for match, name in zip(boolean_matches, dataset["names"]) if match)
        if votes:
            face_estimation = votes.most_common(1)[0][0]
            # Add recognized face to training data for more accuracy
            if os.path.isdir(f"{datapath}/training/{face_estimation}"):
                cv2.imwrite(f"{datapath}/training/{face_estimation}/{datetime.now().strftime('%Y%m%d%H%M%S')}.png", orig_png)
            return face_estimation
        else:
            return "unknown user"

if __name__ == "__main__":
    data_path = f"{os.path.realpath(os.path.dirname(__file__))}/face_data"
    encoding_path = f"{data_path}/encoding.pkl"
    model = "hog" # Better for use with CPU rather than GPU

    train_new_face(data_path)
    #print(recognize_face(data_path, encoding_path, model))

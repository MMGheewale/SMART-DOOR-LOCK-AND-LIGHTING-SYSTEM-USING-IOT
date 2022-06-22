import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)
from threading import Thread

import face_recognition
import picamera
import numpy as np

ON = False
OFF = True

lock=7
GPIO.setmode(GPIO.BOARD)
GPIO.setup(lock,GPIO.OUT)
GPIO.output(lock,OFF)

def camera_code():
    camera = picamera.PiCamera()
    camera.resolution = (320, 240)
    output = np.empty((240, 320, 3), dtype=np.uint8)

    # Load a sample picture and learn how to recognize it.
    print("Loading known face image(s)")
    obama_image = face_recognition.load_image_file("maaz.jpg")
    obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

    # Initialize some variables
    face_locations = []
    face_encodings = []
    
    while True:
        print("Capturing image.")
        # Grab a single frame of video from the RPi camera as a numpy array
        camera.capture(output, format="rgb")
    
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(output)
        print("Found {} faces in image.".format(len(face_locations)))
        face_encodings = face_recognition.face_encodings(output, face_locations)
    
        # Loop over each face found in the frame to see if it's someone we know.
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            match = face_recognition.compare_faces([obama_face_encoding], face_encoding)
            name = "<Unknown Person>"
    
            if match[0]:
                name = "Maaz Gheewale"
                print("I see someone named {}!".format(name))
                GPIO.output(lock,ON)
                time.sleep(10);
                GPIO.output(lock,OFF)
            else:
                print("I see someone named {}!".format(name))
    
get_level_thread = Thread(target = camera_code)
get_level_thread.daemon = True
get_level_thread.start()

class keypad():
    def __init__(self, columnCount = 3):

        # CONSTANTS 
        if columnCount is 3:
            self.KEYPAD = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                ["*",0,"#"]
            ]

            self.ROW         = [40,38,36,37]
            self.COLUMN      = [35,33,31]
        
        elif columnCount is 4:
            self.KEYPAD = [
                [1,2,3,"A"],
                [4,5,6,"B"],
                [7,8,9,"C"],
                ["*",0,"#","D"]
            ]

            self.ROW         = [28,27,26,23]
            self.COLUMN      = [22,21,30,21]
        else:
            return
     
    def getKey(self):
         
        # Set all columns as output low
        for j in range(len(self.COLUMN)):
            GPIO.setup(self.COLUMN[j], GPIO.OUT)
            GPIO.output(self.COLUMN[j], GPIO.LOW)
         
        # Set all rows as input
        for i in range(len(self.ROW)):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
        # Scan rows for pushed key/button
        # A valid key press should set "rowVal"  between 0 and 3.
        rowVal = -1
        for i in range(len(self.ROW)):
            tmpRead = GPIO.input(self.ROW[i])
            if tmpRead == 0:
                rowVal = i
                 
        # if rowVal is not 0 thru 3 then no button was pressed and we can exit
        if rowVal <0 or rowVal >3:
            self.exit()
            return
         
        # Convert columns to input
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
         
        # Switch the i-th row found from scan to output
        GPIO.setup(self.ROW[rowVal], GPIO.OUT)
        GPIO.output(self.ROW[rowVal], GPIO.HIGH)
 
        # Scan columns for still-pushed key/button
        # A valid key press should set "colVal"  between 0 and 2.
        colVal = -1
        for j in range(len(self.COLUMN)):
            tmpRead = GPIO.input(self.COLUMN[j])
            if tmpRead == 1:
                colVal=j
                 
        # if colVal is not 0 thru 2 then no button was pressed and we can exit
        if colVal <0 or colVal >2:
            self.exit()
            return
 
        # Return the value of the key pressed
        self.exit()
        return self.KEYPAD[rowVal][colVal]
         
    def exit(self):
        # Reinitialize all rows and columns as input at exit
        for i in range(len(self.ROW)):
                GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP) 
        for j in range(len(self.COLUMN)):
                GPIO.setup(self.COLUMN[j], GPIO.IN, pull_up_down=GPIO.PUD_UP)
         
if __name__ == '__main__':
    # Initialize the keypad class
    kp = keypad()
    i=0
    password=[1,2,3,4]
    checkpass=[]
    # Loop while waiting for a keypress
    digit = None
    while True:
        digit = kp.getKey()
        if(digit!=None):
            i+=1
            checkpass.append(digit)
            print(digit)
            time.sleep(0.5)
            if(digit=="*"):
                i=0
                checkpass=[]
            if(i==4):
                if((checkpass[0]==password[0]) and (checkpass[1]==password[1]) and (checkpass[2]==password[2])  and (checkpass[3]==password[3])):
                    print("lockopen")
                    GPIO.output(lock,ON)
                    time.sleep(10);
                    GPIO.output(lock,OFF)
                    print("lock close")
                    i=0
                    checkpass=[]
                elif((checkpass[0]!=password[0]) or (checkpass[1]==password[1]) or (checkpass[2]!=password[2])  or (checkpass[3]!=password[3])):
                    print("Incorrect Password")
                    i=0
                    checkpass=[]
                else:
                    GPIO.cleanup()

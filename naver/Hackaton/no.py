import cv2
import os

count =0

dir = os.path.abspath("./mv")
fname = os.listdir(dir)
fdir = os.path.join(dir, fname[0])


vidcap = cv2.VideoCapture(fdir)
while True:
      success,image = vidcap.read()
      if not success:
          break
      print ('Read a new frame: ', success)
      fname = "{}.jpg".format("{0:05d}".format(count))
      cv2.imwrite("./mvimages/frame%d.jpg" % count, image) # save frame as JPEG file
      count += 1

    #cv2.imwrite("./mvimages/frame%d.jpg" % count, image)
vidcap.release()

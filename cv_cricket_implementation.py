# -*- coding: utf-8 -*-
"""CV_Cricket_implementation.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1pvl8LGyeTTw_ZHYdKG7GyyMdFuYoabf_
"""

from google.colab import drive
drive.mount("/content/drive", force_remount=True)

import os
os.chdir('/content/drive/MyDrive/Mask_RCNN/samples')
dir = os.getcwd()
print(dir)

# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow
print(tensorflow.__version__)

import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf 
import tensorflow.keras as keras
from keras.applications.resnet50 import ResNet50
from keras.applications.vgg16 import VGG16
from keras.layers import Flatten, Input
from keras.models import Model
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
import numpy as np
import pandas as pd
import time
import cv2

ROOT_DIR = os.getcwd()
print(ROOT_DIR)
import warnings
warnings.filterwarnings("ignore")

sys.path.append(ROOT_DIR)  
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
import coco

os.chdir('/content/drive/MyDrive/Mask_RCNN/samples/videos')
ROOT_DIR = os.getcwd()
print(ROOT_DIR)

import cv2
import numpy as np


def random_colors(N):
    np.random.seed(1)
    colors = [tuple(255 * np.random.rand(3)) for _ in range(N)]
    return colors


def apply_mask(image, mask, color, alpha=0.5):
    """apply mask to image"""
    for n, c in enumerate(color):
        image[:, :, n] = np.where(
            mask == 1,
            image[:, :, n] * (1 - alpha) + alpha * c,
            image[:, :, n] 
        )
    return image


def apply_mask_3(image, mask, color, alpha=0.5):
    """apply mask to image"""
    for n, c in enumerate(color):
        image[:, :, n] = np.where(
            mask == 1,
            image[:, :, n] * (1 - alpha),
            image[:, :, n] 
        )
    return image



def apply_mask_2(image, mask, color):
  for n,c in enumerate(color):
    image[:, :, n] = np.where(mask ==1, image[:,:,n] , image[:,:,n]*0 )

  return image  

def display_instances(image, boxes, masks, ids, names, scores):
    """
        take the image and results and apply the mask, box, and Label
    """
    n_instances = boxes.shape[0]
    colors = random_colors(n_instances)

    if not n_instances:
        print('NO INSTANCES TO DISPLAY')
    else:
        assert boxes.shape[0] == masks.shape[-1] == ids.shape[0]

    for i, color in enumerate(colors):
        if not np.any(boxes[i]):
            continue

        y1, x1, y2, x2 = boxes[i]
        label = names[ids[i]]
        if (label == 'person' or label == 'sports ball' or label == 'baseball bat'):
          score = scores[i] if scores is not None else None
          caption = '{} {:.2f}'.format(label, score) if score else label
          mask = masks[:, :, i]
          image = apply_mask(image, mask, color)
          # image = cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
          # image = cv2.putText(
          # image, caption, (x1, y1), cv2.FONT_HERSHEY_COMPLEX, 0.7, color, 2
          # )



    imagex = np.zeros(image.shape)
    for i in range(boxes.shape[0]):
      image_temp = np.zeros(image.shape)
      for j in range(image.shape[2]):
          image_temp[:,:,j] = image[:,:,j] * masks[:,:,i]
          imagex = cv2.bitwise_or(imagex, image_temp)

      # plt.figure(figsize=(8,8))
      # plt.imshow(image_temp)
    

    # print(boxes)

    return imagex     


  

if __name__ == '__main__':
    """
        test everything
    """
    import os
    import sys
    from mrcnn import utils
    import mrcnn.model as modellib
    #sys.path.append(os.path.join(ROOT_DIR, "samples/coco/"))  # To find local version
    print(os.getcwd())
    from coco import coco
    
    batch_size = 1
    ROOT_DIR = os.getcwd()
    MODEL_DIR = os.path.join(ROOT_DIR, "logs")
    VIDEO_DIR = os.path.join(ROOT_DIR, "save2")
    VIDEO_SAVE_DIR = os.path.join(VIDEO_DIR, 'video_out')
    COCO_MODEL_PATH = os.path.join(ROOT_DIR, "mask_rcnn_coco.h5")
    if not os.path.exists(COCO_MODEL_PATH):
        utils.download_trained_weights(COCO_MODEL_PATH)
        
    class InferenceConfig(coco.CocoConfig):
        GPU_COUNT = 1
        IMAGES_PER_GPU = batch_size

    config = InferenceConfig()
    config.display()

    model = modellib.MaskRCNN(
        mode="inference", model_dir=MODEL_DIR, config=config
    )
    model.load_weights(COCO_MODEL_PATH, by_name=True)
    class_names = [
        'BG', 'person', 'bicycle', 'car', 'motorcycle', 'airplane',
        'bus', 'train', 'truck', 'boat', 'traffic light',
        'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird',
        'cat', 'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear',
        'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie',
        'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
        'kite', 'baseball bat', 'baseball glove', 'skateboard',
        'surfboard', 'tennis racket', 'bottle', 'wine glass', 'cup',
        'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
        'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
        'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed',
        'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
        'keyboard', 'cell phone', 'microwave', 'oven', 'toaster',
        'sink', 'refrigerator', 'book', 'clock', 'vase', 'scissors',
        'teddy bear', 'hair drier', 'toothbrush'
    ]
    
    # for j in range(35, 36):
    capture = cv2.VideoCapture(os.path.join(VIDEO_DIR, 'test'+ '.mp4'))
    try:
        if not os.path.exists(VIDEO_SAVE_DIR):
            os.makedirs(VIDEO_SAVE_DIR)
    except OSError:
        print ('Error: Creating directory of data')

    frames = []
    frame_count = 0
    # these 2 lines can be removed if you dont have a 1080p camera.
    #capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    #capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    dir = os.path.join(VIDEO_SAVE_DIR)
    if not os.path.exists(dir):
            os.makedirs(dir)

    while True:
        ret, frame = capture.read()
        # Bail out when the video file ends
        if not ret:
            break
        
        # Save each frame of the video to a list
        frame_count += 1
        frames.append(frame)
        print('frame_count :{0}'.format(frame_count))
        if len(frames) == batch_size:
            results = model.detect(frames, verbose=0)
            print('Predicted')
            for i, item in enumerate(zip(frames, results)):
                frame = item[0]
                r = item[1]
                frame = display_instances(
                    frame, r['rois'], r['masks'], r['class_ids'], class_names, r['scores']
                )
                name = '{0}.jpg'.format(frame_count + i - batch_size)
                name = os.path.join(VIDEO_SAVE_DIR, name)
                
                cv2.imwrite(name, frame)
                print('writing to file:{0}'.format(name))
            # Clear the frames array to start the next batch
            frames = []

    capture.release()

video = cv2.VideoCapture(os.path.join(VIDEO_DIR, 'test' + '.mp4'));

# Find OpenCV version
(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')

if int(major_ver)  < 3 :
  fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
  print("Frames per second using video.get(cv2.cv.CV_CAP_PROP_FPS): {0}".format(fps))
else :
  fps = video.get(cv2.CAP_PROP_FPS)
  print("Frames per second using video.get(cv2.CAP_PROP_FPS) : {0}".format(fps))

video.release();

def make_video(outvid, images=None, fps=25, size=None,
               is_color=True, format="FMP4"):
    """
    Create a video from a list of images.
 
    @param      outvid      output video
    @param      images      list of images to use in the video
    @param      fps         frame per second
    @param      size        size of each frame
    @param      is_color    color
    @param      format      see http://www.fourcc.org/codecs.php
    @return                 see http://opencv-python-tutroals.readthedocs.org/en/latest/py_tutorials/py_gui/py_video_display/py_video_display.html
 
    The function relies on http://opencv-python-tutroals.readthedocs.org/en/latest/.
    By default, the video will have the size of the first image.
    It will resize every image to this size before adding them to the video.
    """
    from cv2 import VideoWriter, VideoWriter_fourcc, imread, resize
    fourcc = VideoWriter_fourcc(*format)
    vid = None
    for image in images:
        if not os.path.exists(image):
            raise FileNotFoundError(image)
        img = imread(image)
        if vid is None:
            if size is None:
                size = img.shape[1], img.shape[0]
            vid = VideoWriter(outvid, fourcc, float(fps), size, is_color)
        if size[0] != img.shape[1] and size[1] != img.shape[0]:
            img = resize(img, size)
        vid.write(img)
    vid.release()
    return vid


# Directory of images to run detection on
ROOT_DIR = os.getcwd()
VIDEO_DIR = os.path.join(ROOT_DIR, "save2")
VIDEO_SAVE_DIR = os.path.join(VIDEO_DIR, "video_out")
images = list(glob.iglob(os.path.join(VIDEO_SAVE_DIR, '*.*')))
# Sort the images by integer index
images = sorted(images, key=lambda x: float(os.path.split(x)[1][:-3]))

outvid = os.path.join(VIDEO_DIR, "video_out.mp4")
make_video(outvid, images, fps=25)



MODEL_DIR = os.path.join(ROOT_DIR, "logs")
model = keras.models.load_model(os.path.join(MODEL_DIR, 'model_mask_rcnn.h5'))

model1 = ResNet50(weights='imagenet', pooling=max, include_top = False)

shot = {0:'Straight Drive' ,
        1: 'Cover_Drive' , 
        2: 'Pull Shot',
        3: 'Leg Glance'}

test_features = []
path = os.path.join(ROOT_DIR,'save2','video_out')
for i in range(0,45):
  img_path = os.path.join(path,str(i) + '.jpg')
  img = image.load_img(img_path, target_size=(224, 224))
  img_data = image.img_to_array(img)
  img_data = np.expand_dims(img_data, axis=0)
  img_data = preprocess_input(img_data)
  resnet_feature = model1.predict(img_data)
  test_features.append(resnet_feature.squeeze())

testX = np.array(test_features).reshape(1,45,-1)

y_pred = model.predict(testX)
y_pred = np.argmax(y_pred, axis = 1)
print(shot[y_pred[0]])




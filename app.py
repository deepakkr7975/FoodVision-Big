###1. Imports and classnames setup
import gradio as gr
import os
import torch
from model import create_effnetb2_model
from timeit import default_timer as timer
from typing import Tuple,Dict

with open("class_names.txt","r") as f:
    class_names=[food.strip() for food in f.readlines()]
    
effnetb2,effnetb2_transforms=create_effnetb2_model(num_classes=len(class_names))

#load saved weigths
effnetb2.load_state_dict(
    torch.load(f"pretrained_effnetb2_feature_extractor_food101_20_percent.pth",
               map_location=torch.device="cpu")
)

def predict(img)->Tuple[Dict,float]:
  start_time=timer()
  img=effnetb2_transforms(img).unsqueeze(0) #unsqueeze=add batch dimension on 0th
  effnetb2.eval()
  with torch.inference_mode():
    pred_probs=torch.softmax(effnetb2(img),dim=1)
  pred_labels_and_probs={class_names[i]:float(pred_probs[0][i]) for i in range (len(class_names))}

  end_time=timer()
  pred_time=round(end_time-start_time,4)
  return pred_labels_and_probs,pred_time

title='FoodVision BIG 👁️'
description="An EfficientnetB2 feature extractor computer vision model to classify 101 classes of food images"
article="Created By Deepak kr"


example_list=[["examples/" + example ] for example in os.listdir("examples")]

#create a gradio demo
demo=gr.Interface(fn=predict,#maps input to output
                  inputs=gr.Image(type="pil"),
                  outputs=[gr.Label(num_top_classes=5,label="Predictions"),
                           gr.Number(label="Prediction time(s)")],
                  examples=example_list,
                  title=title,
                  description=description,
                  article=article)
demo.launch(debug=False)

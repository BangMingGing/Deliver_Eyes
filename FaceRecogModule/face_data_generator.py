import torch
import cv2 as cv
import numpy as np

from . import model_total as mymodels
from configuration import FACE_CONFIG

device = torch.device('cuda')
model = mymodels.resnet_test(mymodels.AutoCompressor(64, 32))
model.to(device)
model.load_state_dict(torch.load(f"{FACE_CONFIG.PTH_ROUTE}"), strict=False)
model.eval()
torch.set_grad_enabled(False)

async def generate_face_data(user):
    train_data_route = f"{FACE_CONFIG.TRAIN_DATAS_ROUTE}/{user}"
    receiver_info_route = f"{FACE_CONFIG.RECEIVER_INFOS_ROUTE}/{user}"
    
    targets = torch.zeros(1, 2048)
    targets = targets.to(device)
    
    cap = cv.VideoCapture(train_data_route)
    # train_datas = glob.glob(f'{train_data_route}/*.jpg')
    while True:
        if not cap.isOpened():
            print("Failed to open the camera")
            continue
        
        ret, x = cap.read()
        if ret:
            x = cv.resize(x, (224, 224))
            x = x.transpose((2, 0, 1))
            x = np.expand_dims(x, 0)
            x = x.astype(np.float32)
            x = torch.from_numpy(x)
            x = x.to(device)
            targets += model(x)
            targets = torch.round(targets/2, decimals=5)
        else:
            break
    
    targets = targets.unsqueeze(0)
    targets = targets.unsqueeze(0)
    
    torch.save(targets, receiver_info_route)
    return


import numpy as np
import torch
import pytorch_ssim
from onnxruntime import InferenceSession

from . import database

class onnx_server_model:
    def __init__(self, provider):
        self.model = InferenceSession(f"/home/bmk/repos/etri/Deliver_Eyes/FaceRecogModule/resnet_server.onnx",
                                      providers=[f'{provider}ExecutionProvider'])

    def inference(self, out):
        return self.model.run(None, {'input': out})[0]

class Server_Inferer():
    def __init__(self):
        self.provider = 'CUDA'  # CPU or CUDA
        self.model = onnx_server_model(self.provider)

        self.preds_list = {}


    def post_inference(self, drone_name, tensor):
        preds = self.model.inference(tensor)
        if drone_name not in self.preds_list:
            self.preds_list[drone_name] = [preds]
        elif drone_name in self.preds_list:
            self.preds_list[drone_name].append(preds)
        print('inferenc finished')
        return


    async def get_face_recog_result(self, drone_name, receiver):
        result = None
        if drone_name not in self.preds_list:
            result = False
            database.update_face_recog_result_to_mission_file(drone_name, result, None)
            return result
            
        ssim_loss = pytorch_ssim.SSIM(window_size = 11)
        r_mse = []
            
        target_route = f"/home/bmk/repos/etri/Deliver_Eyes/FaceRecogModule/receiver_infos/{receiver}"
        targets = torch.load(target_route)
        
        for preds in self.preds_list[drone_name]:
            preds = torch.Tensor(preds)
            preds = preds.unsqueeze(0)
            preds = preds.unsqueeze(0)
            #se = mse_cal(preds, targets)
            se = ssim_loss(preds.cpu(), targets.cpu())
            r_mse.append(se)

        mse = np.mean(r_mse, axis = 0)
        
        print(f"******** {receiver}'s mse: {mse} ************")
        if mse > 0.5:
            result = True
        else:
            result = False

        database.update_face_recog_result_to_mission_file(drone_name, mse, result)

        return result
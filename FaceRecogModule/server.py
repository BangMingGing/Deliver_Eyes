import numpy as np
import torch
import pytorch_ssim
from onnxruntime import InferenceSession

import database
from configuration import FACE_CONFIG

class onnx_server_model:
    def __init__(self, provider):
        self.model = InferenceSession(f"{FACE_CONFIG.ONNX_ROUTE}",
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
        if drone_name not in self.preds_list:
            database.update_face_recog_result_to_mission_file(drone_name, round(0, 2), False)
            return False
            
        ssim_loss = pytorch_ssim.SSIM(window_size = 11)
        r_mse = []
            
        target_route = f"{FACE_CONFIG.RECEIVER_INFOS_ROUTE}/{receiver}"
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

        database.update_face_recog_result_to_mission_file(drone_name, float(round(mse, 2)), result)
        del self.preds_list[drone_name]

        return result
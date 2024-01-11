import asyncio
import signal
import sys

import database

from server import Server_Inferer

async def face_consume(server_inferer):
    server_inferer = Server_Inferer()
    print(" -- [Face Consumer] started")
    try:
        while True:
            message = database.getFaceMessage()
            if message is not None:
                drone_name = message['drone_name']
                header = message['header']
                contents = message['contents']

                if header == 'face_recog':
                    print('face recog called')
                    tensor = contents['tensor']
                    server_inferer.post_inference(drone_name, tensor)

                elif header == 'face_recog_finish':
                    print('face recog finish called')
                    receiver = contents['receiver']
                    face_recog_result = await server_inferer.get_face_recog_result(drone_name, receiver)
                    new_message = {'header': 'face_inference_finish', 'drone_name': drone_name, 'contents': {'face_recog_result': face_recog_result}}
                    database.send_to_task_module(new_message)

                print('message complete')
            await asyncio.sleep(1)
    except:
        return

async def main():
    loop = asyncio.get_event_loop()

    server_inferer = Server_Inferer()

    consumer_task = loop.create_task(face_consume(server_inferer))

    try:
        await asyncio.gather(consumer_task)
    except KeyboardInterrupt:
        pass
    finally:
        loop.stop()
        loop.run_forever()
        loop.close()


if __name__ == "__main__":
    asyncio.run(main())
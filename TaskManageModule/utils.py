async def get_mission_start_messages(mission, direction, receiver):
    messages = []
    messages.append({
        'header': 'upload_mission', 
        'contents': {'mission': mission, 'direction': direction}
    })
    if receiver != None:
        messages.append({
            'header': 'upload_receiver',
            'contents': {'receiver': receiver}
        })
    takeoff_alt = mission[0][2]
    messages.append({
    'header': 'takeoff',
    'contents': {'takeoff_alt': takeoff_alt}
    })
    messages.append({
        'header': 'start_mission',
        'contents': {}
    })
    return messages

async def get_face_recog_start_message():
    message = {
        'header': 'face_recog_start',
        'contents': {}
    }
    return message

async def get_land_message():
    message = {
        'header': 'land',
        'contents': {}
    }
    return message

async def get_mission_pause_message():
    message = {
        'header': 'pause_mission',
        'contents': {}
    }
    return message

async def get_resume_message():
    message = {
        'header': 'start_mission',
        'contents': {}
    }
    return message

async def get_hover_node_return_message(mission, direction):
    messages = []
    messages.append({
        'header': 'upload_mission', 
        'contents': {'mission': mission, 'direction': direction}
    })
    messages.append({
        'header': 'start_mission',
        'contents': {}
    })
    return messages
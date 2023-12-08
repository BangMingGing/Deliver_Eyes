async def get_mission_start_messages(mission, direction):
    messages = []
    messages.append({
        'header': 'upload_mission', 
        'contents': {'mission': mission, 'direction': direction}
    })
    messages.append({
    'header': 'takeoff',
    'contents': {'takeoff_alt': 10}
    })
    messages.append({
        'header': 'start_mission',
        'contents': {}
    })
    return messages

async def get_forward_mission_finished_message():
    message = {
        'header': 'land',
        'contents': {}
    }
    return message

async def get_reverse_mission_finished_message():
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
import { updateGPS, initGPS } from "./draw.js";

// baseCampLocation 가져오기
export async function getBasecamp() {
    const response = await fetch('/map/getBasecamp');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const basecamp = responseData.basecamp;
        console.log('getBasecamp successful');
        return basecamp;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getBasecamp failed', errors);
    }
}

// nodesLocations 가져오기
export async function getNodes() {
    const response = await fetch('/map/getNodes');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const nodes = responseData.nodes;
        console.log('getNodes successful');
        return nodes;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getNodes failed', errors);
    }
}

// 드론 선정
export async function select_use_drone(payload, destination) {
    const response = await fetch('/map/select_use_drone', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            payload,
            destination
        }),
    });
    const responseData = await response.json();
    if (response.ok) {
        // select_use_drone 성공 처리
        const drone_path_data = responseData.drone_path_data;
        console.log('select drone and path successful');
        return new Promise((resolve) => {
            resolve(drone_path_data);
        })
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('select use_drone failed', errors);
    }
}

export async function path4draw(path) {
    const response = await fetch('/map/path4draw', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            path
        }),
    });

    const responseData = await response.json();
    if (response.ok) {
        // path4draw 성공 처리
        const path_coor = responseData.path_coor;
        console.log('path4draw successful');
        return new Promise((resolve) => {
            resolve(path_coor);
        })
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('path4draw failed', errors);
    }
}


// 경로 생성 요청
export async function generateMissionFile(use_drone, path) {
    const response = await fetch('/map/generateMissionFile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            use_drone,
            path
        }),
    });
    if (response.ok) {
        // generateMissionFile 성공 처리
        console.log('generateMissionFile successful');
    } else {
        // 오류 처리
        console.error('generateMissionFile failed');
    }
}

export async function deliverStartRequest() {
    const response = await fetch('/map/deliverStart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        }),
    });

    if (response.ok) {
        // deliverStart 성공 처리
        console.log('deliverStart successful');
    } else {
        // 오류 처리
        console.error('deliverStart failed');
    }
}

export function startGPSMonitoring(map) {
    // 임의의 gps-point 소스 생성
    initGPS(map)
    
    const eventSource = new EventSource("/map/gps_streaming");

    eventSource.onmessage = function (event) {
        const gpsData = JSON.parse(event.data);
        // gps-point 소스 업데이트
        updateGPS(map, gpsData);
    };
    eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
    };
}

export async function receiveCompleteRequest() {
    const response = await fetch('/map/receiveComplete', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        }),
    });

    if (response.ok) {
        // receiveComplete 성공 처리
        console.log('receiveComplete successful');
    } else {
        // 오류 처리
        console.error('receiveComplete failed');
    }
}
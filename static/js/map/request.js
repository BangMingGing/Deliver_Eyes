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

// 경로 생성 요청
export async function generateMissionFile(basecamp, destination) {
    const response = await fetch('/map/generateMissionFile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            basecamp,
            destination
        }),
    });

    const responseData = await response.json();

    if (response.ok) {
        // generateMissionFile 성공 처리
        const route = responseData.route;
        console.log('generateMissionFile successful');
        return new Promise((resolve) => {
            resolve(route);
        })

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
        // generateMissionFile 성공 처리
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
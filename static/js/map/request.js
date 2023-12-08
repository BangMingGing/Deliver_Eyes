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

// 미션파일 생성 요청
export async function generateMissionFileRequest(payload, destination) {
    const response = await fetch('/map/generateMissionFile', {
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
        // generateMissionFileRequest 성공 처리
        console.log('generateMissionFileRequest successful');
        return new Promise((resolve) => {
            resolve(responseData);
        })
    } else {
        // 오류 처리
        console.error('generateMissionFileRequest failed');
    }
}

// 배송 시작 요청
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

// GPS 모니터링 시작
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

// 수령 완료 요청
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
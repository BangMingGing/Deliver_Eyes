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
export function startGPSMonitoring(map, setFlag) {
    // 임의의 gps-point 소스 생성
    initGPS(map)
    
    const eventSource = new EventSource("/map/gps_streaming");

    eventSource.onmessage = function (event) {
        const eventData = JSON.parse(event.data);
        // gps-point 소스 업데이트
        updateGPS(map, eventData.gps_data);
        // face_recog_start_flag 확인
        const faceRecogFlag = eventData.face_recog_start_flag;
        if (faceRecogFlag) {
            setFlag(faceRecogFlag);
        }
    };
    eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
    };
}

// 얼굴인식 시작 요청
export async function faceRecogStartRequest() {
    const response = await fetch('/map/faceRecogStart', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
        }),
    });

    if (response.ok) {
        // faceRecogStart 성공 처리
        console.log('faceRecogStart successful');
    } else {
        // 오류 처리
        console.error('faceRecogStart failed');
    }
}

// 얼굴인식 결과 모니터링 시작
export function startFaceRecogResultMonitoring(faceRecogResultCallback) {
    
    const eventSource = new EventSource("/map/face_recog_result_streaming");

    eventSource.onmessage = function (event) {
        const eventData = JSON.parse(event.data);
        // face_recog_result 확인
        const face_recog_result = eventData.face_recog_result;
        if (face_recog_result != null) {
            faceRecogResultCallback(face_recog_result);
            eventSource.close();
        }
    };
    eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
    };
}

// 비밀번호로 인증 요청
export async function passwordCertifyRequest(password) {
    const response = await fetch('/map/passwordCertify', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            password
        }),
    });

    if (response.ok) {
        // passwordCertify 성공 처리
        console.log('passwordCertify successful');
        return new Promise((resolve) => {
            resolve(true);
        })
    } else {
        // 오류 처리
        console.error('passwordCertify failed');
        return new Promise((resolve) => {
            resolve(false);
        })
    }
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
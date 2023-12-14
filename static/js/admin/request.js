import { updateGPS, drawRoute, removeRouteAndPoint, deleteAllRouteSource } from "./draw.js";
import { getStorageDroneNames, insertStorageDroneNames, deleteStorageDroneNames } from "./utils.js";

let eventSource;

// baseCampLocation 가져오기
export async function getBasecamp() {
    const response = await fetch('/admin/getBasecamp');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const basecamps = responseData.basecamps;
        console.log('getBasecamp successful');
        return basecamps;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getBasecamp failed', errors);
    }
}

// nodesLocations 가져오기
export async function getNodes() {
    const response = await fetch('/admin/getNodes');

    const responseData = await response.json();

    if (response.ok) {
        // getNodes 성공 처리
        const nodes = responseData.nodes;
        console.log('getNodes successful');
        return nodes;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getNodes failed', errors);
    }
}

export async function insertnode(selectedLocationName,selectedLocation,neighbor_node_list) {
    const response = await fetch('/admin/insertnode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            selectedLocationName,
            selectedLocation,
            neighbor_node_list
        }),
    });
}

export async function addNewneighbor(selectedLocationName,neighbor_node_list) {
    const response = await fetch('/admin/addNewneighbor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            selectedLocationName,
            neighbor_node_list
        }),
    });
}

export async function delete_node(node_name) {
    const response = await fetch('/admin/delete_node', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            node_name
        }),
    });
    
    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const node_name = responseData.node_name;
        console.log('get delete_node_name successful');
        return node_name;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('get delete_node_name failed', errors);

    }
}

export async function drawGraph() {
    const response = await fetch('/admin/drawGraph');
    const responseData = await response.json();
    if (response.ok) {
        // drawGraph  성공 처리
        const message = responseData.message;
        console.log('drawGraph successful');
        return message;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('drawGraphe failed', errors);

    }
}

export async function InitUI() {    
    const response = await fetch('/admin/InitUI');
    const responseData = await response.json();
    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const dronedata = responseData.dronedata;
        console.log('get dronedata successful');
        return dronedata;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('get dronedata failed', errors);

    }
}

export async function updateUI(map) {
    if (eventSource) {
        eventSource.close();
        eventSource = undefined;
        console.log("Closed existing EventSource.");
        deleteAllRouteSource(map)
        return;
    }
    eventSource = new EventSource("/admin/updateUI");
    async function handleEvent(event) {
        const storageDroneNames = await getStorageDroneNames(); // 비동기 함수 호출
        const streamingData = JSON.parse(event.data);
        const streamingDroneNames = Object.keys(streamingData);

        // 신규 드론 감지 및 처리
        streamingDroneNames.forEach(newDroneName => {
            if (!storageDroneNames.includes(newDroneName)) {
                console.log("detect new input drone: ", newDroneName);
                const route = streamingData[newDroneName]?.mission || [];
                console.log("---------Draw new route---------");
                drawRoute(map, newDroneName, route); // 지도에 루트 그리기
                insertStorageDroneNames(newDroneName); // 로컬 스토리지에 드론 이름 추가
            }
        });

        // 삭제 
        const missingDroneName = storageDroneNames.filter(drone => !streamingDroneNames.includes(drone));
        if (missingDroneName.length > 0) {
            console.log("detect mission clear drone : ", missingDroneName);
            missingDroneName.forEach(droneName => {
                console.log("---------Remove Route---------");
                removeRouteAndPoint(map, droneName);
                deleteStorageDroneNames(droneName);
            });
        }

        updateGPS(map, streamingData);
    }

    eventSource.onmessage = handleEvent;
    eventSource.onerror = function (error) {
        console.error("EventSource failed:", error);
        eventSource.close();
    };
}
import { getBasecamp, getNodes, generateMissionFile, deliverStartRequest } from "./request.js";
import { setDestinationMode, getSelectedLocation, setDefaultMode, findClosestNode } from "./utils.js";
import { drawMap, drawMarker, drawMarkers, drawDestinationMarker, drawRoute } from "./draw.js";

async function main() {
    let basecamp;
    let nodes;
    let map;
    // 목적지 선택 모드인지 확인하는 변수
    let isSelectingDestination = false;
    let destination;
    let destinationMarker;
    let route;
    
    // 맵 초기화
    basecamp = await getBasecamp();
    nodes = await getNodes();
    map = await drawMap(basecamp);
    drawMarker(map, basecamp);
    drawMarkers(map, nodes);


    const selectNodeButton = document.getElementById('selectNodeButton');
    const generateMissionFileButton = document.getElementById('generateMissionFileButton');
    const deliverStartButton = document.getElementById('deliverStartButton');
    const receiveCompleteButton = document.getElementById('receiveCompleteButton');
    
    selectNodeButton.addEventListener('click', async function() {
        let selectedLocation;

        isSelectingDestination = await setDestinationMode(map, isSelectingDestination);
        selectedLocation = await getSelectedLocation(map);
        if (isSelectingDestination) {
            // 추가 노드 마커 그리기
            destinationMarker = drawDestinationMarker(map, selectedLocation, destinationMarker);
            // 미션파일 생성 버튼 활성화
            generateMissionFileButton.disabled = false;            
        }
        isSelectingDestination = await setDefaultMode(map, isSelectingDestination);
    });

    generateMissionFileButton.addEventListener('click', async function() {
        // 미션파일 생성 요청
        route = await generateMissionFile(basecamp, destination);
        // 경로 그리기
        drawRoute(map, route);
        // 배송 시작 버튼 활성화
        deliverStartButton.disabled = false;
    })

    deliverStartButton.addEventListener('click', async function() {
        // 배송 시작 요청
        await deliverStartRequest();
        // GPS 모니터링 시작
        // GPS 값 요청 시작
    });
    receiveCompleteButton.addEventListener('click', async function() {
        // 백엔드로 복귀 요청
        
        // 후 처리 과정
    });
}

main();
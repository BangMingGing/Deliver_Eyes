import { getBasecamp, getNodes, generateMissionFile } from "./request.js";
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


    const selectDestinationButton = document.getElementById('selectDestinationButton');
    const generateMissionFileButton = document.getElementById('generateMissionFileButton');
    const deliverStartButton = document.getElementById('deliverStartButton');
    const receiveCompleteButton = document.getElementById('receiveCompleteButton');
    
    selectDestinationButton.addEventListener('click', async function() {
        let selectedLocation;

        isSelectingDestination = await setDestinationMode(map, isSelectingDestination);
        selectedLocation = await getSelectedLocation(map);
        if (isSelectingDestination) {
            // 근접 노드 찾아 destination으로 설정
            destination = await findClosestNode(selectedLocation, nodes);
            // 목적지 마커 그리기
            destinationMarker = drawDestinationMarker(map, destination, destinationMarker);
            // 미션파일 생성 버튼 활성화
            generateMissionFileButton.disabled = false;            
        }
        isSelectingDestination = await setDefaultMode(map, isSelectingDestination);
    });

    generateMissionFileButton.addEventListener('click', async function() {
        // 경로 생성 요청
        route = await generateMissionFile(basecamp, destination);
        // 경로 그리기
        drawRoute(map, route);
    })

    deliverStartButton.addEventListener('click', async function() {
        // 
    });
    // receiveCompleteButton.addEventListener('click', receiveCompleteButtonEvent);
}

main();
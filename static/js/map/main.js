import { getBasecamp, getNodes, generateMissionFileRequest, deliverStartRequest, startGPSMonitoring, receiveCompleteRequest } from "./request.js";
import { setDestinationMode, getSelectedLocation, setDefaultMode, findClosestNode, displayMessage, sendMessage, isValidNumber } from "./utils.js";
import { drawMap, drawMarker, drawMarkers, drawDestinationMarker, drawRoute } from "./draw.js";

async function main() {
    let basecamp;
    let nodes;
    let map;
    // 목적지 선택 모드인지 확인하는 변수
    let isSelectingDestination = false;
    // 미션파일 관련 변수
    let destination;
    let destinationMarker;
    let payload;
    // 맵 초기화
    basecamp = await getBasecamp();
    nodes = await getNodes();
    map = await drawMap(basecamp);
    drawMarker(map, basecamp);
    drawMarkers(map, nodes);


    //chatbox
    const chatInput = document.getElementById('chatInput');
    const messageSendButton = document.getElementById('messageSend');

    const OrderingButton = document.getElementById('OrderingButton');
    const selectDestinationButton = document.getElementById('selectDestinationButton');
    const generateMissionFileButton = document.getElementById('generateMissionFileButton');
    const deliverStartButton = document.getElementById('deliverStartButton');
    const receiveCompleteButton = document.getElementById('receiveCompleteButton');
   
    chatInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            sendMessage(chatInput);
        }
    });

    messageSendButton.addEventListener('click', async function(){
        sendMessage(chatInput);
    });

    OrderingButton.addEventListener('click', async function () {
        payload = await prompt("Please input your Shipping Weight(kg)");
        if (!isValidNumber(payload)) {
            displayMessage(`Invalid input. Please enter a valid number.`);
        } else {
            displayMessage(`Payload Weight: ${payload}kg`);
            payload = parseFloat(payload);
            selectDestinationButton.disabled = false;
        }
    });

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
        let missionFileInfo = await generateMissionFileRequest(payload, destination);
        if (missionFileInfo != null) {
            drawRoute(map, missionFileInfo.route);
            let drone_name =  missionFileInfo.drone_name;
            displayMessage(`Service drone : ${drone_name}`);
            displayMessage(`Mission file upload successful`);
            // 배송 시작 버튼 활성화
            deliverStartButton.disabled = false;
        } else {
            displayMessage(`Mission file upload failed. Please retry`);
        }
        
    })

    deliverStartButton.addEventListener('click', async function() {
        displayMessage(`Delivery Start`);
        // 배송 시작 요청
        await deliverStartRequest();
        // GPS 모니터링 시작
        startGPSMonitoring(map)
        // 수령 완료 버튼 활성화
        OrderingButton.disabled = true;
        selectDestinationButton.disabled = true;
        generateMissionFileButton.disabled = true;
        receiveCompleteButton.disabled = false;
    });
    receiveCompleteButton.addEventListener('click', async function() {
        // 백엔드로 복귀 요청
        displayMessage('Delivery completed');
        await receiveCompleteRequest();
        // 후 처리 과정
    });
}

main();
import { getBasecamp, getNodes, generateMissionFile, deliverStartRequest, select_use_drone, path4draw, startGPSMonitoring, receiveCompleteRequest } from "./request.js";
import { setDestinationMode, getSelectedLocation, setDefaultMode, findClosestNode, displayMessage, sendMessage,isValidNumber,sendPayloadToServer } from "./utils.js";
import { drawMap, drawMarker, drawMarkers, drawDestinationMarker, drawRoute } from "./draw.js";

async function main() {
    let basecamp;
    let nodes;
    let map;
    // 목적지 선택 모드인지 확인하는 변수
    let isSelectingDestination = false;
    let destination;
    let destinationMarker;
    let use_drone;
    let payload;
    let data = [];
    let path = [];
    let altitudes;
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
        const shippingWeight = prompt("Please input your Shipping Weight(kg)");
        if (shippingWeight === null || !isValidNumber(shippingWeight)) {
            displayMessage("Invalid input. Please enter a valid number.");
        } else {
            displayMessage(`Shipping Weight: ${shippingWeight}kg`);
            payload = parseFloat(shippingWeight);
            sendPayloadToServer(payload);
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
        data = await select_use_drone(payload, destination)
        use_drone =  data[0]
        path = data[1]
        altitudes = data[2]
        displayMessage(`service drone : ${use_drone}`);
        displayMessage(`path : ${path}`);

        path = await path4draw(path)
        drawRoute(map, path);
        
        path = path.map((point, index) => [...point, altitudes[index]]);
        generateMissionFile(use_drone, path);
        displayMessage(`Mission file upload successfulcce`);
        // 배송 시작 버튼 활성화
        deliverStartButton.disabled = false;
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
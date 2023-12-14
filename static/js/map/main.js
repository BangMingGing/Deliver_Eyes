import { getBasecamp, getNodes, generateMissionFileRequest, deliverStartRequest, startGPSMonitoring, faceRecogStartRequest, startFaceRecogResultMonitoring, passwordCertifyRequest, receiveCompleteRequest } from "./request.js";
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
    const faceRecogStartButton = document.getElementById('faceRecogStartButton')
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
            await displayMessage(`Invalid input. Please enter a valid number.`);
        } else {
            await displayMessage(`Payload Weight: ${payload}kg`);
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
            await displayMessage(`Service drone : ${drone_name}`);
            await displayMessage(`Mission file upload successful`);
            // 배송 시작 버튼 활성화
            deliverStartButton.disabled = false;
        } else {
            await displayMessage(`Mission file upload failed. Please retry`);
        }
        
    })

    deliverStartButton.addEventListener('click', async function() {
        // 상위 버튼 비활성화
        OrderingButton.disabled = true;
        selectDestinationButton.disabled = true;
        generateMissionFileButton.disabled = true;
        deliverStartButton.disabled = true;
        await displayMessage(`Delivery Start`);
        // 배송 시작 요청
        await deliverStartRequest();
        // GPS 모니터링 시작, 목적지 도착 시 얼굴인식 버튼 활성화
        let faceRecogFlag;
        await new Promise((resolve) => {
            startGPSMonitoring(map, function(flag) {
                faceRecogFlag = flag;
                resolve();
            });
        });
        // 얼굴인식 가능 시 
        if (faceRecogFlag) {
            await displayMessage('Drone reached at destination hovering altitude.');
            await displayMessage('Press Face Recog Start Button');
            faceRecogStartButton.disabled = false;
        }
    });
    
    faceRecogStartButton.addEventListener('click', async function() {
        faceRecogStartButton.disabled = true;
        // 얼굴인식 시작 요청
        await faceRecogStartRequest();
        // 얼굴인식 결과 모니터링
        let faceRecogResult;
        await new Promise((resolve) => {
            startFaceRecogResultMonitoring(function(result) {
                faceRecogResult = result;
                resolve();
            });
        });
        // 얼굴인식 결과에 따른 처리
        if (faceRecogResult) {
            // 얼굴인식 성공 처리
            await displayMessage('Face recognition succeeded. Drone is landing');
            await displayMessage('After receiving the item and securing a safe distance');
            await displayMessage('And then press the Receive Done buttons');
            receiveCompleteButton.disabled = false;
        } else {
            // 얼굴인식 실패 처리
            await displayMessage('Face recognition failed. Please input your password');
            const password = await prompt("Please input your password");
            // 비밀번호 검증 요청
            const passwordCertifyResult = await passwordCertifyRequest(password);
            if (passwordCertifyResult) {
                // 비밀번호 검증 성공 처리
                await displayMessage('Password Certify Successed. Drone is landing');
                await displayMessage('After receiving the item and securing a safe distance');
                await displayMessage('And then press the Receive Done buttons');
                receiveCompleteButton.disabled = false;
            } else {
                // 비밀번호 검증 실패 처리
                await displayMessage('Password Certify failed. Drone return to home');
            }
        }
        
    })

    receiveCompleteButton.addEventListener('click', async function() {
        // 백엔드로 복귀 요청
        await displayMessage('Delivery completed');
        await receiveCompleteRequest();
        await displayMessage('Drone return to home');
        // 후 처리 과정
        receiveCompleteButton.disabled = true;
    });
}

main();
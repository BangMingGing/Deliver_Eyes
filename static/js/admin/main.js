import { getBasecamp, getNodes, insertnode, addNewneighbor, delete_node, drawGraph,InitUI, updateUI } from "./request.js";
import { setDestinationMode, getSelectedLocation, getDistance, setDefaultMode, select_neighbor_node, getMaxBuildingHeight, getDeletedNodeNames, setDeletedNodeNames, setStorageDroneNames } from "./utils.js";
import { toggleNodeEditButtons, toCheckDeliveryButton, drawMap, drawBCMarker, drawMarkers, drawDestinationMarker, drawmakenode, drawRoute, drawRoutes } from "./draw.js";

async function main() {
    let basecamps;
    let nodes;
    let map;

    let isNodeEditEnabled = false; // 초기 상태: 노드 편집이 비활성화된 상태
    let ischeckdeliverEnabled = false;
    // 목적지 선택 모드인지 확인하는 변수
    let isSelectingDestination = false;

    let selectedLocation;
    let destinationMarker;
    let markers = [];
    let sourceCounter = 0;
    let neighbor_node_list = [];
    let selectedLocationName;
    let delete_node_name = [];
    // 맵 초기화
    basecamps = await getBasecamp();
    nodes = await getNodes();
    map = await drawMap(basecamps[0].BC_coor);
    markers = drawBCMarker(map, basecamps, markers);
    markers = drawMarkers(map, nodes, markers);


    const EditNodeButton = document.getElementById('EditNodeButton')
    const CheckDeliveryButton = document.getElementById('CheckDeliveryButton');

    const selectNodeButton = document.getElementById('selectNodeButton');
    const completeNodeButton = document.getElementById('completeNodeButton');
    const set_neighbor_node = document.getElementById('set_neighbor_node');
    const CompleteButton = document.getElementById('CompleteButton');
    const NodeDeleteButton = document.getElementById('NodeDeleteButton');




    EditNodeButton.addEventListener('click', async function() {
        isNodeEditEnabled = await toggleNodeEditButtons(isNodeEditEnabled, EditNodeButton)
    });

    CheckDeliveryButton.addEventListener('click', async function() {
        ischeckdeliverEnabled = await toCheckDeliveryButton(map, ischeckdeliverEnabled, CheckDeliveryButton)
        const deliverdronesinfo = await InitUI()
        const drone_names = deliverdronesinfo.map(droneInfo => droneInfo.drone_name);
        setStorageDroneNames(drone_names)
        drawRoutes(map, deliverdronesinfo);
        updateUI(map)
    });


    selectNodeButton.addEventListener('click', async function() {

        isSelectingDestination = await setDestinationMode(map, isSelectingDestination);
        selectedLocation = await getSelectedLocation(map);
        if (isSelectingDestination) {
            // 추가 노드 마커 그리기
            destinationMarker = drawDestinationMarker(map, selectedLocation, destinationMarker);
            // 미션파일 생성 버튼 활성화
            completeNodeButton.disabled = false;            
        }
        isSelectingDestination = await setDefaultMode(map, isSelectingDestination);
    });

    completeNodeButton.addEventListener('click', async function() {
        drawmakenode(map, selectedLocation,destinationMarker)
        set_neighbor_node.disabled = false;
    })


    set_neighbor_node.addEventListener('click', async function() {
        isSelectingDestination = await setDestinationMode(map, isSelectingDestination);
        if (isSelectingDestination){
            const neighbor_node = await select_neighbor_node(markers) 

            const neighbor_node_name = neighbor_node.nodeName
            const neighbor_node_coor = neighbor_node.coordinate

            const max_height = await getMaxBuildingHeight(map, selectedLocation, neighbor_node.coordinate, 5)
            const distance = await getDistance(selectedLocation[1],selectedLocation[0],neighbor_node_coor[1],neighbor_node_coor[0])

            const route = [selectedLocation, neighbor_node_coor]

            sourceCounter = drawRoute(map, route, sourceCounter)

            neighbor_node_list.push([neighbor_node_name, max_height, distance])
        }
        isSelectingDestination = await setDefaultMode(map, isSelectingDestination);
        CompleteButton.disabled = false;
    });


    CompleteButton.addEventListener('click', async function() {
        delete_node_name = await getDeletedNodeNames()
        if(delete_node_name > 0){
            selectedLocationName = delete_node_name.pop()
            insertnode(selectedLocationName,selectedLocation,neighbor_node_list)
            addNewneighbor(selectedLocationName, neighbor_node_list)
            setDeletedNodeNames(delete_node_name)
        }
        else{
            selectedLocationName = Number(nodes.length) + 1
            insertnode(selectedLocationName,selectedLocation,neighbor_node_list)
            addNewneighbor(selectedLocationName, neighbor_node_list)
        }
        drawGraph()
        location.reload()
    });


    NodeDeleteButton.addEventListener('click', async function() {
        const deletenode = await select_neighbor_node(markers)
        const node_name = await delete_node(deletenode.nodeName)
        delete_node_name.push(node_name)
        setDeletedNodeNames(delete_node_name)
        drawGraph()
        location.reload()
    });
}

main();
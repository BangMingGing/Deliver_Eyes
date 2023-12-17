
export async function setDestinationMode(map, isSelectingDestination) {
    return new Promise(async (resolve) => {
        if (!isSelectingDestination) {
            map.getCanvas().style.cursor = 'crosshair';
            isSelectingDestination = true;
            resolve(isSelectingDestination);
        } else {
            // 이미 목적지 선택 모드라면 취소
            map.getCanvas().style.cursor = 'default';
            isSelectingDestination = false;
            resolve(isSelectingDestination);
        }
    })
}

export async function getSelectedLocation(map) {
    return new Promise((resolve) => {
        map.once('click', function(e) {
            // 클릭한 지점의 좌표 반환
            const selectedLocation = e.lngLat;

            resolve([selectedLocation['lng'], selectedLocation['lat']]);
        });
    })
}

export async function setDefaultMode(map, isSelectingDestination) {
    return new Promise((resolve) => {
        map.getCanvas().style.cursor = 'default';
        isSelectingDestination = false;
        resolve(isSelectingDestination);
    })
}

export async function findClosestNode(selectedLocation, nodesLocations) {
    if (!selectedLocation || !nodesLocations || nodesLocations.length === 0) {
        return null;
    }

    const selectedLat = selectedLocation[1];
    const selectedLon = selectedLocation[0];
    
    let closestNode = null;
    let closestDistance = Number.MAX_VALUE;

    for (const nodeLocation of nodesLocations) {
        const nodeLat = nodeLocation[1];
        const nodeLon = nodeLocation[0];

        const distance = await getDistance(selectedLat, selectedLon, nodeLat, nodeLon);

        if (distance < closestDistance) {
            closestDistance = distance;
            closestNode = nodeLocation;
        }
    }

    return new Promise((resolve) => {
        resolve(closestNode);
    })
}

//노드 간 거리 계산
export async function getDistance(lat1, lon1, lat2, lon2) {
    // 지구 반경 (km)
    const R = 6373.0;

    const radians = (degrees) => degrees * (Math.PI / 180);

    lat1 = radians(lat1);
    lon1 = radians(lon1);
    lat2 = radians(lat2);
    lon2 = radians(lon2);

    const latDiff = lat1 - lat2;
    const lonDiff = lon1 - lon2;

    const a =
        Math.sin(latDiff / 2) ** 2 +
        Math.cos(lat1) *
        Math.cos(lat2) *
        Math.sin(lonDiff / 2) ** 2;

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

    const distance = R * c * 1000; // Radius of the Earth in kilometers
    return distance
}

// 특정 좌표에서 건물의 고도를 가져오는 함수
function getBuildingHeightAtCoordinate(map, coordinate) {

    const intersectedFeatures = map.queryRenderedFeatures(map.project(coordinate), {
        layers: ['add-3d-buildings'],
    });

    let buildingHeight = 0;

    intersectedFeatures.forEach(feature => {
        const height = feature.properties.height || 0;
        if (height > buildingHeight) {
            buildingHeight = height;
        }
    });

    return buildingHeight;
}

// 노드 2개를 잇는 직선 위의 interval(m) 간격으로 존재하는 노드들의 배열을 만드는 함수
function getCoordinatesBetweenPoints(point1, point2, interval) {
    const lineString = turf.lineString([point1, point2]);
    const length = turf.length(lineString, { units: 'meters' });
    
    const coordinates = [];
    
    for (let i = 0; i <= length; i += interval) {
        const alongLine = turf.along(lineString, i, { units: 'meters' });
        coordinates.push(alongLine.geometry.coordinates);
    }

    return coordinates;
}

// 출발 노드와 도착 노드 간의 최대 고도를 구하는 함수
export async function getMaxBuildingHeight(map, selectedLocation, neighbor_node, interval) {
    const node1 = selectedLocation;
    const node2 = neighbor_node;

    // 두 지점 사이의 좌표를 가져옵니다.
    const coordinates = getCoordinatesBetweenPoints(node1, node2, interval);

    let maxBuildingHeight = 0;
    coordinates.forEach(coord => {
        // 좌표에서 건물의 고도를 확인합니다.
        const buildingHeight = getBuildingHeightAtCoordinate(map, coord);

        // 현재까지의 최대 고도와 비교하여 갱신합니다.
        if (buildingHeight > maxBuildingHeight) {
            maxBuildingHeight = buildingHeight;
        }
    });
    maxBuildingHeight = maxBuildingHeight + 10
    return new Promise((resolve) => {
        resolve(maxBuildingHeight);
    })
}

// 현재 표시된 노드 선택 후 노드 이름 반환
export async function select_neighbor_node(markers) {
    return new Promise((resolve) => {
        markers.forEach(marker => {
            const markerElement = marker.getElement();

            markerElement.addEventListener('click', function () {
                // 마커의 좌표 가져오기
                const markerLngLat = marker.getLngLat();
                
                // 경도 및 위도 추출
                const longitude = markerLngLat.lng;
                const latitude = markerLngLat.lat;

                console.log('Marker clicked at coordinates:', [longitude, latitude]);

                // Popup 내용을 직접 접근
                const popupContent = marker.getPopup()._content;

                // 여기에서 클릭한 마커의 정보를 활용하여 노드 이름을 가져옵니다.
                const nodeName = popupContent.querySelector('h1').innerText;
                console.log('Clicked marker:', nodeName);

                // 노드 이름 및 좌표를 resolve로 전달
                resolve({ nodeName, coordinate: [longitude, latitude] });
            });
        });
    });
}

// 로컬 스토리지에서 삭제된 노드 이름을 가져오는 함수
export async function getDeletedNodeNames() {
    return new Promise((resolve, reject) => {
        try {
            // 비동기 작업 수행 (예: localStorage에서 데이터 가져오기)
            const storedNames = localStorage.getItem('deletedNodeNames');
            const resultArray = storedNames ? JSON.parse(storedNames) : [];

            // 비동기 작업 완료 후 resolve에 결과 전달
            resolve(resultArray);
        } catch (error) {
            // 에러가 발생하면 reject에 에러 전달
            reject(error);
        }
    });
}

// for node delete

// 로컬 스토리지에 삭제된 노드 이름을 저장하는 함수
export async function setDeletedNodeNames(names) {
    localStorage.setItem('deletedNodeNames', JSON.stringify(names));
}


// 로컬 스토리지에서 미션 파일에 저장된 드론 이름을 가져오는 함수
export async function getStorageDroneNames() {
    const storedData = localStorage.getItem('dronenames');
    
    // 저장된 데이터가 있을 경우 JSON 파싱하여 반환
    if (storedData) {
        return JSON.parse(storedData);
    }
    
    // 저장된 데이터가 없을 경우 빈 배열 반환 또는 다른 기본값 반환
    return [];
}

// for monitoring


// 로컬 스토리지에 미션 파일에 저장된 드론 이름을 저장하는 함수
export async function setStorageDroneNames(drone_names) {
    localStorage.setItem('dronenames', JSON.stringify(drone_names));
}

export async function insertStorageDroneNames(drone_name) {
    // 로컬 스토리지에서 드론 이름 배열을 가져오기
    const existingDroneNames = await getdronenames();
    // 특정 drone_name을 배열에 추가하고 새로운 배열 생성
    const updatedDroneNames = existingDroneNames.concat(drone_name);
    // 로컬 스토리지에 업데이트된 배열 저장
    setStorageDroneNames(updatedDroneNames);
}



export async function deleteStorageDroneNames(drone_name) {
    // 로컬 스토리지에서 드론 이름 배열을 가져오기
    const existingDroneNames = await getdronenames();
    // 특정 drone_name을 배열에서 제거
    const updatedDroneNames = existingDroneNames.filter(name => name !== drone_name);
    // 로컬 스토리지에 업데이트된 배열 저장
    console.log("updatedDroneNames :  ",updatedDroneNames)
    setStorageDroneNames(updatedDroneNames);
}




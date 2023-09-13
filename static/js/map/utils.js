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

async function getDistance(lat1, lon1, lat2, lon2) {
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

    const distance = R * c; // Radius of the Earth in kilometers

    return distance
}
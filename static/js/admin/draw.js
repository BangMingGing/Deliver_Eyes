export function toggleNodeEditButtons(isNodeEditEnabled) {
    isNodeEditEnabled = !isNodeEditEnabled; // 토글 버튼 상태 변경
    if (isNodeEditEnabled) {
        // 노드 편집이 활성화된 경우
        document.getElementById("selectNodeButton").style.display = "inline-block";
        document.getElementById("completeNodeButton").style.display = "inline-block";
        document.getElementById("set_neighbor_node").style.display = "inline-block";
        document.getElementById("CompleteButton").style.display = "inline-block";
        document.getElementById("NodeDeleteButton").style.display = "inline-block";
        EditNodeButton.textContent = "노드 편집 취소";

        // 배송 상태 확인 버튼을 숨김
        document.getElementById("CheckDeliveryButton").style.display = "none";
    } else {
        // 노드 편집이 비활성화된 경우
        document.getElementById("selectNodeButton").style.display = "none";
        document.getElementById("completeNodeButton").style.display = "none";
        document.getElementById("set_neighbor_node").style.display = "none";
        document.getElementById("CompleteButton").style.display = "none";
        document.getElementById("NodeDeleteButton").style.display = "none";
        EditNodeButton.textContent = "노드 편집";
        // 배송 상태 확인 버튼을 나타냄
        document.getElementById("CheckDeliveryButton").style.display = "inline-block";
    }
    return new Promise((resolve) => {
        resolve(isNodeEditEnabled);
    })
}

export function toCheckDeliveryButton(map, ischeckdeliverEnabled, CheckDeliveryButton) {
    ischeckdeliverEnabled = !ischeckdeliverEnabled; // 토글 버튼 상태 변경
    if (ischeckdeliverEnabled) {
        // 노드 편집을 숨김
        document.getElementById("EditNodeButton").style.display = "none";
        console.log("non diplay editnode button")
        CheckDeliveryButton.textContent = "배송 상태 확인 취소";

    } else {
        // 노드 편집을 나타냄
        document.getElementById("EditNodeButton").style.display = "inline-block";
        console.log("diplay editnode button")
        CheckDeliveryButton.textContent = "배송 상태 확인";
    }
    return new Promise((resolve) => {
        resolve(ischeckdeliverEnabled);
    })
}

export function deleteAllRouteSource(map) {
    // Get the map layers
    const layers = map.getStyle().layers || [];

    // Remove layers starting with 'drone-' or 'route-'
    layers.forEach(layer => {
        if (layer.id && (layer.id.startsWith('drone-') || layer.id.startsWith('route-'))) {
            map.removeLayer(layer.id);
        }
    });

    // Get the map sources
    const sources = map.getStyle().sources || {};

    // Remove sources starting with 'drone-' or 'route-'
    Object.keys(sources).forEach(source => {
        if (source && (source.startsWith('drone-') || source.startsWith('route-'))) {
            map.removeSource(source);
        }
    });
}


export async function drawMap(basecamp) {
    mapboxgl.accessToken = 'pk.eyJ1IjoibWluZ3VlbmNobyIsImEiOiJjbGdveW1sNjMwaGhuM3NxbTIxdWs1b3N2In0.6Zgzs_gXXFCRY5oVK_Ziww';
    const map = new mapboxgl.Map({
        // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
        style: 'mapbox://styles/mapbox/light-v11',
        center: basecamp,
        zoom: 15.5,
        pitch: 45,
        bearing: -17.6,
        container: 'map',
        antialias: true
    });

    map.on('style.load', () => {
        // Insert the layer beneath any symbol layer.
        const layers = map.getStyle().layers;
        const labelLayerId = layers.find(
            (layer) => layer.type === 'symbol' && layer.layout['text-field']
        ).id;

        // The 'building' layer in the Mapbox Streets
        // vector tileset contains building height data
        // from OpenStreetMap.
        map.addLayer(
            {
                'id': 'add-3d-buildings',
                'source': 'composite',
                'source-layer': 'building',
                'filter': ['==', 'extrude', 'true'],
                'type': 'fill-extrusion',
                'minzoom': 15,
                'paint': {
                    'fill-extrusion-color': '#aaa',

                    // Use an 'interpolate' expression to
                    // add a smooth transition effect to
                    // the buildings as the user zooms in.
                    'fill-extrusion-height': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        15.05,
                        ['get', 'height']
                    ],
                    'fill-extrusion-base': [
                        'interpolate',
                        ['linear'],
                        ['zoom'],
                        15,
                        0,
                        15.05,
                        ['get', 'min_height']
                    ],
                    'fill-extrusion-opacity': 0.6
                }
            },
            labelLayerId
        );
    });
       // 우측 상단에 NavigationControl 생성.
       const nav = new mapboxgl.NavigationControl();
       map.addControl(nav, 'top-right');
   
       // 맵 반환
       return new Promise((resolve) => {
           resolve(map);
       })
}


export function drawBCMarker(map, basecamps, markers) {
    basecamps.forEach(basecamp => {
        const { BC_name, BC_coor } = basecamp;
        const marker = new mapboxgl.Marker({ color: 'blue' })
            .setLngLat(BC_coor)
            .setPopup(new mapboxgl.Popup().setHTML(`<h1>${BC_name}</h1>`))
            .addTo(map);
            markers.push(marker)    
    });
    return markers;
}


export function drawMarkers(map, nodes, markers) {
    nodes.forEach(node => {
        const { node_name, node_coor } = node;

        const marker = new mapboxgl.Marker({ color: 'red' })
            .setLngLat(node_coor)
            .setPopup(new mapboxgl.Popup().setHTML(`<h1>${node_name}</h1>`))
            .addTo(map);
            markers.push(marker)    
    });
    return markers;

}


export function drawDestinationMarker(map, destination, destinationMarker) {
    // 이미 목적지 마커가 있는 경우 해당 마커를 삭제
    if (destinationMarker) {
        destinationMarker.remove();
    }

    // 새로운 목적지 마커 생성
    destinationMarker = new mapboxgl.Marker({ color: 'green' })
        .setLngLat(destination)
        .setPopup(new mapboxgl.Popup().setHTML("<h1>Destination</h1>"))
        .addTo(map);

    // 목적지 마커 반환
    return destinationMarker;
}

export function drawmakenode(map, selectedLocation, destinationMarker) {
    // green 마커 삭제
    if (destinationMarker) {
        destinationMarker.remove();
    }

    // 추가된 노드 마커 생성
    destinationMarker = new mapboxgl.Marker({ color: 'red' })
        .setLngLat(selectedLocation)
        .setPopup(new mapboxgl.Popup().setHTML("<h1>node</h1>"))
        .addTo(map);

    // 노드 마커 반환
    return destinationMarker;
}

function getDroneColor(droneName) {
    if (droneName === 'low_drone') {
        return 'blue';
    } else if (droneName === 'middle_drone') {
        return 'red';
    } else {
        return 'green';
    }
}

export function removeRouteAndPoint(map, droneName) {
    const routeLayerId = `route-${droneName}`;
    const pointLayerId = `drone-${droneName}`;

    // 만약 같은 드론 이름을 가진 레이어와 소스가 있다면 삭제
    if (map.getLayer(routeLayerId)) {
        map.removeLayer(routeLayerId);
    }

    if (map.getSource(routeLayerId)) {
        map.removeSource(routeLayerId);
    }

    // 포인트 레이어와 소스 삭제
    if (map.getLayer(pointLayerId)) {
        map.removeLayer(pointLayerId);
    }

    if (map.getSource(pointLayerId)) {
        map.removeSource(pointLayerId);
    }
}

export function drawRoute4setneighbor(map, route, sourceCounter) {
    if (!map || !route || route.length === 0) {
        console.error('Invalid map or route data.');
        return;
    }

    // 소스 ID 생성
    const sourceId = 'route-source-' + sourceCounter++;

    const geojson = {
        type: 'Feature',
        geometry: {
            type: 'LineString',
            coordinates: route,
        },
    };

    // 레이어에 추가할 데이터 소스 생성
    map.addSource(sourceId, {
        type: 'geojson',
        data: geojson,
    });

    // 위에서 생성한 소스로 레이어 생성
    map.addLayer({
        id: sourceId,
        type: 'line',
        source: sourceId, // 소스 ID 사용
        layout: {
            'line-join': 'round',
            'line-cap': 'round',
        },
        paint: {
            'line-color': 'blue',
            'line-width': 3,
        },
    });
    console.log(sourceCounter)
    return sourceCounter
}

export function drawRoute(map, droneName, route) {
        console.log("route : ", route)
        const routeLayerId = `route-${droneName}`;

        // 만약 같은 드론 이름을 가진 레이어와 소스가 있다면 삭제
        if (map.getLayer(routeLayerId)) {
            map.removeLayer(routeLayerId);
        }

        if (map.getSource(routeLayerId)) {
            map.removeSource(routeLayerId);
        }

        // 새로운 소스와 레이어 추가
        map.addSource(routeLayerId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'LineString',
                    coordinates: route
                },
                properties: {}
            }
        });

        map.addLayer({
            id: routeLayerId,
            type: 'line',
            source: routeLayerId,
            paint: {
                'line-color': getDroneColor(droneName),
                'line-width': 3
            }
        });
}

export function drawRoutes(map, data) {
    data.forEach(droneData => {
        const droneName = droneData.drone_name;
        const route = droneData.mission;

        const layerId = `drone-${droneName}`;

        // 만약 같은 드론 이름을 가진 레이어와 소스가 있다면 삭제
        if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
        }

        if (map.getSource(layerId)) {
            map.removeSource(layerId);
        }

        // 새로운 소스와 레이어 추가
        map.addSource(layerId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: [0,0]
                },
                properties: {}
            }
        });

        map.addLayer({
            id: layerId,
            type: 'circle',
            source: layerId,
            paint: {
                'circle-color': getDroneColor(droneName),
                'circle-radius': 6
            }
        });

        // 추가: route 그리기
        const routeLayerId = `route-${droneName}`;

        // 만약 같은 드론 이름을 가진 레이어와 소스가 있다면 삭제
        if (map.getLayer(routeLayerId)) {
            map.removeLayer(routeLayerId);
        }

        if (map.getSource(routeLayerId)) {
            map.removeSource(routeLayerId);
        }

        // 새로운 소스와 레이어 추가
        map.addSource(routeLayerId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'LineString',
                    coordinates: route
                },
                properties: {}
            }
        });

        map.addLayer({
            id: routeLayerId,
            type: 'line',
            source: routeLayerId,
            paint: {
                'line-color': getDroneColor(droneName),
                'line-width': 3
            }
        });
    });
}


export function updateGPS(map, data) {
    // 추가사항: 받아온 data를 기반으로 드론 이름 별로 route에 해당하는 배열을 line으로 그리기 (있다면 삭제하고 다시 그리기)
    Object.keys(data).forEach(droneName => {
        const droneData = data[droneName];
        const gpsData = droneData.gps_data;
        console.log("gpsData : ", gpsData)
        const layerId = `drone-${droneName}`;

        // 만약 같은 드론 이름을 가진 레이어와 소스가 있다면 삭제
        if (map.getLayer(layerId)) {
            map.removeLayer(layerId);
        }

        if (map.getSource(layerId)) {
            map.removeSource(layerId);
        }

        // 새로운 소스와 레이어 추가
        map.addSource(layerId, {
            type: 'geojson',
            data: {
                type: 'Feature',
                geometry: {
                    type: 'Point',
                    coordinates: gpsData
                },
                properties: {}
            }
        });

        map.addLayer({
            id: layerId,
            type: 'circle',
            source: layerId,
            paint: {
                'circle-color': getDroneColor(droneName),
                'circle-radius': 6
            }
        });
    });
}


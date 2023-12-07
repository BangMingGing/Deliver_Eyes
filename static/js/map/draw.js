export async function drawMap(baseCampLocation) {
    mapboxgl.accessToken = 'pk.eyJ1IjoibWluZ3VlbmNobyIsImEiOiJjbGdveW1sNjMwaGhuM3NxbTIxdWs1b3N2In0.6Zgzs_gXXFCRY5oVK_Ziww';

    // <div id="map">에 map 할당
    const map = new mapboxgl.Map({
        container: 'map',
        style: 'mapbox://styles/mapbox/light-v11',
        // 중심 좌표: 경상국립대
        center: baseCampLocation,
        zoom: 16
    });

    // 우측 상단에 NavigationControl 생성.
    const nav = new mapboxgl.NavigationControl();
    map.addControl(nav, 'top-right');

    // 맵 반환
    return new Promise((resolve) => {
        resolve(map);
    })
}


export function drawMarker(map, location) {
    new mapboxgl.Marker({ color: 'blue' })
        .setLngLat(location)
        .setPopup(new mapboxgl.Popup().setHTML("<h1>BaseCamp</h1>"))
        .addTo(map);
}


export function drawMarkers(map, locations) {
    locations.forEach(location => {
        new mapboxgl.Marker({ color: 'red' })
        .setLngLat(location)
        .setPopup(new mapboxgl.Popup().setHTML("<h1>Service Area</h1>"))
        .addTo(map);
    });
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

export function drawRoute(map, route) {
    if (!map || !route || route.length === 0) {
        console.error('Invalid map or route data.');
        return;
    }

    // 이미 그려진 경로가 있다면 찾아서 지우기
    if (map.getLayer('route')) {
        map.removeLayer('route');
    }
    if (map.getSource('route-source')) {
        map.removeSource('route-source');
    }

    const geojson = {
        type: 'Feature',
        geometry: {
            type: 'LineString',
            coordinates: route,
        },
    };

    // 레이어에 추가할 데이터 소스 생성
    map.addSource('route-source', {
        type: 'geojson',
        data: geojson,
    });

    // 위에서 생성한 소스로 레이어 생성
    map.addLayer({
        id: 'route',
        type: 'line',
        source: 'route-source',
        layout: {
            'line-join': 'round',
            'line-cap': 'round',
        },
        paint: {
            'line-color': 'blue',
            'line-width': 3,
        },
    });
}


export function initGPS(map) {
    map.addSource('drone', {
        type: 'geojson',
        data: {
            type: 'Feature',
            geometry: {
                type: 'Point',
                coordinates: [0, 0]
            },
            properties: {}
        }
    });
      
    map.addLayer({
        id: 'drone',
        type: 'circle',
        source: 'drone',
        paint: {
            'circle-color': 'blue',
            'circle-radius': 6
        }
    });
}

export function updateGPS(map, gpsData) {
    // console.log(gpsData)
    map.getSource('drone').setData({
        type: 'Feature',
        geometry: {
          type: 'Point',
          coordinates: gpsData
        },
        properties: {}
      });
}
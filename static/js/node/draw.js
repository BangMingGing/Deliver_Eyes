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

export function drawRoute(map, route, sourceCounter) {
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



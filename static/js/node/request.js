// baseCampLocation 가져오기
export async function getBasecamp() {
    const response = await fetch('/node/getBasecamp');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const basecamps = responseData.basecamps;
        console.log('getBasecamp successful');
        return basecamps;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getBasecamp failed', errors);
    }
}

// nodesLocations 가져오기
export async function getNodes() {
    const response = await fetch('/node/getNodes');

    const responseData = await response.json();

    if (response.ok) {
        // getNodes 성공 처리
        const nodes = responseData.nodes;
        console.log('getNodes successful');
        return nodes;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getNodes failed', errors);
    }
}

export async function insertnode(selectedLocationName,selectedLocation,neighbor_node_list) {
    const response = await fetch('/node/insertnode', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            selectedLocationName,
            selectedLocation,
            neighbor_node_list
        }),
    });
}

export async function addNewneighbor(selectedLocationName,neighbor_node_list) {
    const response = await fetch('/node/addNewneighbor', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            selectedLocationName,
            neighbor_node_list
        }),
    });
}

export async function delete_node(node_name) {
    const response = await fetch('/node/delete_node', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            node_name
        }),
    });
    
    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const node_name = responseData.node_name;
        console.log('get delete_node_name successful');
        return node_name;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('get delete_node_name failed', errors);

    }
}

export async function drawGraph() {
    const response = await fetch('/node/drawGraph');
    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const message = responseData.message;
        console.log('drawGraph successful');
        return message;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('drawGraphe failed', errors);

    }
}
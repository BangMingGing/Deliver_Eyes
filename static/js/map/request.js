// baseCampLocation 가져오기
export async function getBasecamp() {
    const response = await fetch('/map/getBasecamp');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const basecamp = responseData.basecamp;
        console.log('getBasecamp successful');
        return basecamp;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getBasecamp failed', errors);
    }
}

// nodesLocations 가져오기
export async function getNodes() {
    const response = await fetch('/map/getNodes');

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const nodes = responseData.nodes;
        console.log('getNodes successful');
        return nodes;
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('getNodes failed', errors);
    }
}

// route 가져오기
export async function generateMissionFile(basecamp, destination) {
    const response = await fetch('/map/generateMissionFile', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            basecamp,
            destination
        }),
        credentials: 'include',
    });

    const responseData = await response.json();

    if (response.ok) {
        // getBaseCampLocation 성공 처리
        const route = responseData.route;
        console.log('generateMissionFile successful');
        return new Promise((resolve) => {
            resolve(route);
        });
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('generateMissionFile failed', errors);
    }
}

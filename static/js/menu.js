async function logout() {
    // 로그아웃 기능 추가 필요
    window.location.href = '/login/'
}

// 지도 창으로 이동하는 함수
async function goToMapPage() {
    window.location.href = '/map/';
}

// 얼굴 등록 창으로 이동하는 함수
async function goToFacePage() {
    window.location.href = '/face/';
}

// 관리자 창으로 이동하는 함수
async function goToAdminPage() {
    window.location.href = '/admin/';
}

// 관리자 노드 창으로 이동하는 함수
async function goToAdminNodePage() {
    window.location.href = '/admin_node/';
}

// 노드 창으로 이동하는 함수
async function goToAdminMonitorPage() {
    window.location.href = '/admin_monitor/';
}
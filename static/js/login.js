// 엔터키 이벤트 리스너 추가
// DomContentLoaded는 HTML 컨텐츠가 모두 로드된 후 스크립트가 실행되도록 보장
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('login-form');
        form.addEventListener('keydown', function (event) {
            if (event.key === 'Enter') {
                login();
            }
        });
});

// 로그인
async function login() {
    // 입력한 email, password 받아오기
    const user_email = document.getElementById('user_email').value;
    const password = document.getElementById('password').value;

    // email, password를 body에 넣어 백엔드로 로그인 처리 요청
    const response = await fetch('/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: JSON.stringify({
            user_email,
            password
        }),
    });

    // 요청에 대한 응답
    const responseData = await response.json();

    if (response.ok) {
        // 로그인 성공 처리 - 토큰을 쿠키에 저장, menu 화면으로 이동
        const access_token = responseData.access_token;
        setAccessTokenCookie(access_token);
        console.log('Login successful');
        window.location.href = '/menu/';
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('Login failed', errors);
    }
}

// 토큰을 쿠키에 저장하는 함수
function setAccessTokenCookie(token) {
    const expirationDate = new Date();
    // 쿠키 유효 기간 설정 (예: 1일)
    expirationDate.setDate(expirationDate.getDate() + 1); 
    
    document.cookie = `access_token=${token}; expires=${expirationDate.toUTCString()}; path=/`;
}

// 회원가입 창으로 이동하는 함수
async function goToSignupPage() {
    window.location.href = '/signup/';
}


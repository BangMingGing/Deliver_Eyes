// 회원가입
async function signup() {
    // 입력한 email, password 받아오기
    const user_email = document.getElementById('user_email').value;
    const password = document.getElementById('password').value;

    // email, password를 body에 넣어 백엔드로 회원가입 처리 요청
    const response = await fetch('/signup/', {
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
        // 회원가입 성공 처리 - 로그인 화면으로 이동
        console.log('Login successful');
        window.location.href = '/login/';
    } else {
        // 오류 처리
        const errors = responseData.errors;
        console.error('Login failed', errors);
    }
}
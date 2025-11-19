const loginForm = document.getElementById("login-form")
const loginFeedBack = document.querySelector(".check-valid");
const findPasswordForm = document.getElementById("find-password-form")
const resetPasswordForm = document.getElementById("reset-password-form")

const feedBackMsg = {
    '000': '로그인에 성공했습니다. 잠시만 기다려주세요...',
    '001':  '올바른 아이디와 비밀번호를 입력해주세요.',
    '002': '비밀번호를 잘못 입력했습니다. 다시 시도해주세요.',
    '003': '입력하신 계정은 존재하지 않는 계정입니다.',
    '004': '입력하신 계정은 이메일 인증이 되지 않았습니다.',
    '100': '비밀번호 재설정 링크가 이메일로 전송되었습니다.',
    '103': '비밀번호 찾기에 실패했습니다. 다시 시도해주세요.',
    '200': '비밀번호가 성공적으로 변경되었습니다. 로그인 페이지로 이동합니다...',
    '201': '비밀번호와 비밀번호 확인이 일치하지 않습니다.',
    '202': '비밀번호는 최소 6자 이상이어야 합니다.',
    '203': '비밀번호 재설정에 실패했습니다. 다시 시도해주세요.'
}

// back-end 에 formdata를 전송하고, 그에 대한 결과를 받기 위한 함수.
async function getLoginValidation() {
    try {
        const resultForm = await fetch("login/validation", {
            method: 'POST',
            redirect: 'follow',
            body: new FormData(loginForm)
        })
        return resultForm.json();
    } catch (err) {
        throw new Error(err);
    }
}

// flask 로부터 로그인이 유효한지를 체크하고, 아니라면 오류 메세지를 출력시킴.
async function checkisVaild(event) {
    event.preventDefault();
    const validResult = await getLoginValidation();

    if (validResult.result == 'fail') {
        loginFeedBack.innerText = feedBackMsg[validResult.errcode];
        return;
    }
    // 로그인에 성공했다면, 리다이렉트를 진행시킴.
    loginFeedBack.innerText = feedBackMsg['000'];
    window.location.href = validResult.url;
}

// 비밀번호 찾기 폼 제출 처리
async function getFindPasswordValidation() {
    try {
        const resultForm = await fetch("/register/password", {
            method: 'POST',
            redirect: 'follow',
            body: new FormData(findPasswordForm)
        })
        return resultForm.json();
    } catch (err) {
        throw new Error(err);
    }
}

async function checkFindPasswordValid(event) {
    event.preventDefault();
    const checkValid = document.querySelector('.check-valid');
    const confirmDiv = document.querySelector('.main__find-password--confirm');
    
    try {
        const validResult = await getFindPasswordValidation();
        
        if (validResult.result == 'success') {
            // 폼 숨기기
            document.querySelector('.main__find-password--session').style.display = 'none';
            // 확인 메시지 표시
            if (confirmDiv) {
                confirmDiv.style.display = 'block';
            }
            if (checkValid) {
                checkValid.innerText = feedBackMsg['100'];
            }
        } else {
            if (checkValid) {
                checkValid.innerText = feedBackMsg[validResult.errcode] || feedBackMsg['103'];
            }
        }
    } catch (err) {
        if (checkValid) {
            checkValid.innerText = feedBackMsg['103'];
        }
    }
}

// 비밀번호 재설정 폼 제출 처리
async function getResetPasswordValidation() {
    try {
        const password = document.getElementById('password').value;
        const passwordConfirm = document.getElementById('password_confirm').value;
        
        // 클라이언트 측 유효성 검사
        if (password !== passwordConfirm) {
            return { result: 'fail', errcode: '201' };
        }
        
        if (password.length < 6) {
            return { result: 'fail', errcode: '202' };
        }
        
        const resultForm = await fetch(resetPasswordForm.action, {
            method: 'POST',
            redirect: 'manual',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: new FormData(resetPasswordForm)
        })
        return resultForm.json();
    } catch (err) {
        throw new Error(err);
    }
}

async function checkResetPasswordValid(event) {
    event.preventDefault();
    const checkValid = document.querySelector('.check-valid');
    
    try {
        const validResult = await getResetPasswordValidation();
        
        if (validResult.result == 'success') {
            if (checkValid) {
                checkValid.innerText = feedBackMsg['200'];
            }
            // 성공 시 리다이렉트 또는 메시지 표시
            if (validResult.url) {
                setTimeout(() => {
                    window.location.href = validResult.url;
                }, 2000);
            }
        } else {
            if (checkValid) {
                checkValid.innerText = feedBackMsg[validResult.errcode] || feedBackMsg['203'];
            }
        }
    } catch (err) {
        if (checkValid) {
            checkValid.innerText = feedBackMsg['203'];
        }
    }
}

// 이벤트 리스너 등록
if (loginForm) {
    loginForm.addEventListener('submit', checkisVaild);
}

if (findPasswordForm) {
    findPasswordForm.addEventListener('submit', checkFindPasswordValid);
}

if (resetPasswordForm) {
    resetPasswordForm.addEventListener('submit', checkResetPasswordValid);
}

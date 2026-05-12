document.addEventListener('DOMContentLoaded', () => {
    const socket = io();
    const inputs = document.querySelectorAll('.pin-input');
    const joinBtn = document.getElementById('join-btn');

    inputs.forEach((input, index) => {
        input.addEventListener('input', (e) => {
            e.target.value = e.target.value.replace(/[^a-zA-Z0-9]/g, '');
            if (e.target.value !== '' && index < inputs.length - 1){
                inputs[index + 1].focus();
            }
            const code = Array.from(inputs).map(i => i.value).join('');
            joinBtn.disabled = code.length !== 4;
        });

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Backspace' && e.target.value === '' && index > 0) {
                inputs[index - 1].focus();
                inputs[index - 1].value = '';
            }
        });
    });

    joinBtn.addEventListener('click', () => {
        const code = Array.from(inputs).map(i => i.value).join('');
        joinBtn.disabled = true;
        joinBtn.innerHTML = 'Проверка...';
        socket.emit('join_to_room', { code: code });
    });
    socket.on('join_success', (data) => {
        window.location.href = `/hub?code=${data.code}`;
    });

    socket.on('join_error', (data) => {
        alert(data.msg);
        joinBtn.disabled = false;
        joinBtn.innerHTML = 'Войти в лобби';
    });
});
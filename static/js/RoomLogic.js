document.addEventListener('DOMContentLoaded', () => {
    const socket = io();

    socket.on('connect', () => {
        socket.emit('join', { room: ROOM_CODE });
    });

    socket.on('status', (data) => {
        const msgElement = document.getElementById('msg');
        if (msgElement) msgElement.textContent = data.msg;
    });
    const startBtn = document.getElementById('start-btn');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            startBtn.disabled = true;
            startBtn.innerText = "Запуск игры...";
            socket.emit('game_m', { code: ROOM_CODE });
        });
    }

    socket.on('game_success', (data) => {
        window.location.replace(`/game_m?code=${data.code}`)
    });
});
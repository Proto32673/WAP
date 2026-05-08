document.addEventListener('DOMContentLoaded', () => {
        const socket = io();
        const ROOM_CODE = "{{ code }}";
        const IS_CREATOR = {{ "true" if is_creator else "false" }};
        socket.emit('join', { room: ROOM_CODE });
        socket.on('status', (data) => {
            const list = document.getElementById('players-list');
            list.innerHTML += `<p class="text-success m-1 fw-bold">➔ ${data.msg}</p>`;
        });
}
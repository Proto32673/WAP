let map;
let currentPlacemark = null;
let addMarkerMode = false;

window.socket = io();
window.socket.on('connect', () => {
    window.socket.emit('join', { room: ROOM_CODE });
});

function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        correctLat: parseFloat(params.get('lat')),
        correctLng: parseFloat(params.get('lng')),
        roundId: parseInt(params.get('round_id')),
        locationName: params.get('name')
    };
}

function showNotification(message) {
    const statusSpan = document.getElementById('markerStatus');
    const oldText = statusSpan.innerText;
    statusSpan.innerText = message;
    statusSpan.style.color = '#ffd700';
    setTimeout(() => {
        statusSpan.innerText = oldText;
        statusSpan.style.color = currentPlacemark ? '#28a745' : '#dc3545';
    }, 4000);
}

function updateMarkerStatus() {
    const statusSpan = document.getElementById('markerStatus');
    if (currentPlacemark) {
        const coords = currentPlacemark.geometry.getCoordinates();
        statusSpan.innerHTML = `Метка: ${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}`;
        statusSpan.style.color = '#28a745';
    } else {
        statusSpan.innerHTML = 'Нет метки';
        statusSpan.style.color = '#dc3545';
    }
}

function setPlacemark(lat, lng) {
    if (currentPlacemark) map.geoObjects.remove(currentPlacemark);
    currentPlacemark = new ymaps.Placemark([lat, lng], {}, { preset: 'islands#greenCircleIcon' });
    map.geoObjects.add(currentPlacemark);
    updateMarkerStatus();
}

window.removeCurrentPlacemark = function() {
    if (currentPlacemark) {
        map.geoObjects.remove(currentPlacemark);
        currentPlacemark = null;
        updateMarkerStatus();
    }
};

function disableControls() {
    addMarkerMode = false;
    document.getElementById('addMarkerBtn').disabled = true;
    document.getElementById('clearMarkersBtn').disabled = true;
    document.getElementById('centerMapBtn').disabled = true;
    document.getElementById('answBtn').disabled = true;

    const buttons = document.querySelectorAll('.map-controls .btn');
    buttons.forEach(btn => btn.style.opacity = '0.5');

    map.events.remove('click');
}

function answerQuestion() {
    if (!currentPlacemark) {
        alert('Поставьте метку на карте!');
        return;
    }

    const coords = currentPlacemark.geometry.getCoordinates();
    const params = getUrlParams();



    disableControls();
    showNotification("Ответ отправлен. Ожидаем остальных игроков...");

    window.socket.emit('submit_answer', {
        room: ROOM_CODE,
        lat: coords[0],
        lng: coords[1],
        correctLat: params.correctLat,
        correctLng: params.correctLng
    });
}
if (window.socket) {
    window.socket.on('player_answered_notice', (data) => {
        showNotification(`Игрок ${data.name} готов!`);
    });

    window.socket.on('all_finished', (data) => {

        sessionStorage.setItem('multiplayerResults', JSON.stringify(data));
        window.location.replace('/results');
    });
}

ymaps.ready(function() {
    map = new ymaps.Map('map', { center: [20, 0], zoom: 2, controls: [] });
    map.controls.add('zoomControl', { position: { right: 20, top: 100 } });

    map.events.add('click', function(e) {
        if (addMarkerMode) {
            const coords = e.get('coords');
            setPlacemark(coords[0], coords[1]);
            addMarkerMode = false;
            document.getElementById('addMarkerBtn').style.opacity = '1';
        }
    });

    document.getElementById('addMarkerBtn').addEventListener('click', function() {
        addMarkerMode = true;
        this.style.opacity = '0.7';
    });

    document.getElementById('clearMarkersBtn').addEventListener('click', removeCurrentPlacemark);
    document.getElementById('centerMapBtn').addEventListener('click', () => {
        map.setCenter(currentPlacemark ? currentPlacemark.geometry.getCoordinates() : [20, 0], currentPlacemark ? 10 : 2);
    });

    document.getElementById('answBtn').addEventListener('click', answerQuestion);
    document.getElementById('zoomInBtn').addEventListener('click', () => map.setZoom(map.getZoom() + 1));
    document.getElementById('zoomOutBtn').addEventListener('click', () => map.setZoom(map.getZoom() - 1));
});
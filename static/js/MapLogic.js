let map;
let currentPlacemark = null;
let addMarkerMode = false;

function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        correctLat: parseFloat(params.get('lat')),
        correctLng: parseFloat(params.get('lng')),
        roundId: parseInt(params.get('round_id')),
        locationName: params.get('name')
    };
}

function initGame() {
    const gameParams = getUrlParams();
    sessionStorage.setItem('correctLat', gameParams.correctLat);
    sessionStorage.setItem('correctLng', gameParams.correctLng);
    sessionStorage.setItem('roundId', gameParams.roundId);
    sessionStorage.setItem('locationName', gameParams.locationName || "Неизвестное место");
}

function updateMarkerStatus() {
    const statusSpan = document.getElementById('markerStatus');
    if (currentPlacemark) {
        const coords = currentPlacemark.geometry.getCoordinates();
        statusSpan.innerHTML = `Метка установлена<br>(${coords[0].toFixed(6)}, ${coords[1].toFixed(6)})`;
        statusSpan.style.color = '#28a745';
    } else {
        statusSpan.innerHTML = 'Нет метки';
        statusSpan.style.color = '#dc3545';
    }
}

function setPlacemark(lat, lng) {
    if (currentPlacemark) {
        map.geoObjects.remove(currentPlacemark);
    }

    currentPlacemark = new ymaps.Placemark(
        [lat, lng],
        {
            balloonContent: `<div style="text-align:center;"><strong>Текущая метка</strong><br>Широта: ${lat.toFixed(6)}<br>Долгота: ${lng.toFixed(6)}<br><button onclick="removeCurrentPlacemark()" style="margin-top:8px;padding:5px 12px;background:#dc3545;color:white;border:none;border-radius:5px;cursor:pointer;">Удалить</button></div>`,
            hintContent: `Координаты: ${lat.toFixed(6)}, ${lng.toFixed(6)}`
        },
        { preset: 'islands#greenCircleIcon', iconColor: '#28a745' }
    );

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

function centerMap() {
    if (currentPlacemark) {
        const coords = currentPlacemark.geometry.getCoordinates();
        map.setCenter(coords, 10);
    } else {
        map.setCenter([20, 0], 2);
    }
}

function answerQuestion() {
    if (!currentPlacemark) {
        alert('Сначала установите метку на карте!');
        return;
    }

    const coords = currentPlacemark.geometry.getCoordinates();
    const userLat = coords[0];
    const userLng = coords[1];
    const correctLat = sessionStorage.getItem('correctLat');
    const correctLng = sessionStorage.getItem('correctLng');
    const roundId = sessionStorage.getItem('roundId');
    const locationName = sessionStorage.getItem('locationName');

    // Переход на /ans с передачей всех параметров
    window.location.replace(`/ans?userLat=${userLat}&userLng=${userLng}&correctLat=${correctLat}&correctLng=${correctLng}&roundId=${roundId}&name=${encodeURIComponent(locationName)}`)
}

ymaps.ready(function() {
    initGame();

    map = new ymaps.Map('map', {
        center: [20, 0],
        zoom: 2,
        controls: []
    });

    map.controls.add('zoomControl', { position: { right: 20, top: 100 } });

    const coordDisplay = document.getElementById('coordDisplay');
    map.events.add('mousemove', function(e) {
        const coords = e.get('coords');
        coordDisplay.textContent = `${coords[0].toFixed(6)}, ${coords[1].toFixed(6)}`;
    });

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
        setTimeout(() => {
            if (addMarkerMode) {
                addMarkerMode = false;
                this.style.opacity = '1';
            }
        }, 10000);
    });

    document.getElementById('clearMarkersBtn').addEventListener('click', function() {
        if (currentPlacemark && confirm('Удалить метку?')) {
            removeCurrentPlacemark();
        }
    });

    document.getElementById('centerMapBtn').addEventListener('click', centerMap);
    document.getElementById('answBtn').addEventListener('click', answerQuestion);

    document.getElementById('zoomInBtn').addEventListener('click', () => map.setZoom(map.getZoom() + 1));
    document.getElementById('zoomOutBtn').addEventListener('click', () => map.setZoom(map.getZoom() - 1));
});
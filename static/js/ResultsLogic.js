const rawData = sessionStorage.getItem('multiplayerResults');
if (rawData) {
    const data = JSON.parse(rawData);
    const players = Object.values(data.results);
    const cLat = data.correctLat;
    const cLng = data.correctLng;

    ymaps.ready(() => {
        const map = new ymaps.Map('map', {
            center: [cLat, cLng],
            zoom: 3,
            controls: ['zoomControl']
        });
        const targetMark = new ymaps.Placemark([cLat, cLng], {
            balloonContent: 'Правильный ответ'
        }, {
            preset: 'islands#yellowCircleIcon'
        });
        map.geoObjects.add(targetMark);

        players.sort((a, b) => b.score - a.score);
        const tableHtml = document.getElementById('scoreTable');

        players.forEach((p, index) => {
            const rankClass = index === 0 ? 'rank-1' : '';
            tableHtml.innerHTML += `
                <div class="player-row ${rankClass}">
                    <div class="d-flex align-items-center">
                        <span class="me-3 fw-bold text-white-50">#${index + 1}</span>
                        <div>
                            <div class="fw-bold">${p.name}</div>
                            <div class="dist-label">${Math.round(p.dist)} км от цели</div>
                        </div>
                    </div>
                    <div class="score-display">${p.score} очков</div>
                </div>
            `;

            const pMark = new ymaps.Placemark([p.lat, p.lng], {
                iconCaption: p.name
            }, { preset: 'islands#greenCircleIcon' });

            const line = new ymaps.Polyline([[p.lat, p.lng], [cLat, cLng]], {}, {
                strokeColor: '#28a745', strokeWidth: 2, strokeOpacity: 0.4, style: 'shortdash'
            });

            map.geoObjects.add(pMark);
            map.geoObjects.add(line);
        });

        map.setBounds(map.geoObjects.getBounds(), { checkZoomRange: true, zoomMargin: 50 });

        const HubBtn = document.getElementById('hub-btn');
        if(HubBtn){
            HubBtn.addEventListener('click', () => {
                HubBtn.disabled = true;
                location.href = `/hub?code=${ROOM_CODE}`;
            });
        }
    });
}
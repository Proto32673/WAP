// Получаем координаты из URL
function getUrlParams() {
    const params = new URLSearchParams(window.location.search);
    return {
        userLat: parseFloat(params.get('userLat')),
        userLng: parseFloat(params.get('userLng')),
        correctLat: parseFloat(params.get('correctLat')),
        correctLng: parseFloat(params.get('correctLng')),
        roundId: parseInt(params.get('roundId')),
        locationName: params.get('name')
    };
}

const params = getUrlParams();
let userLat = params.userLat;
let userLng = params.userLng;
let correctLat = params.correctLat;
let correctLng = params.correctLng;
let locationName = params.locationName;

function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon/2) * Math.sin(dLon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    return R * c;
}

function calculateScore(distanceKm) {
    if (distanceKm <= 0) return 10000;
    const alpha = 3100;
    let score = 10000 * Math.exp(-distanceKm / alpha);
    score = Math.round(score);
    return Math.min(10000, Math.max(0, score));
}

function formatDistance(distanceKm) {
    if (distanceKm < 1) {
        return `${Math.round(distanceKm * 1000)} м`;
    } else if (distanceKm < 100) {
        return `${distanceKm.toFixed(1)} км`;
    } else {
        return `${Math.round(distanceKm)} км`;
    }
}

function animateScore(finalScore) {
    const scoreElement = document.getElementById('scoreValue');
    let currentScore = 0;
    const duration = 1000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = finalScore / steps;

    const interval = setInterval(() => {
        currentScore += increment;
        if (currentScore >= finalScore) {
            currentScore = finalScore;
            scoreElement.textContent = Math.round(currentScore);
            clearInterval(interval);
            if (finalScore === 10000) {
                document.getElementById('perfectBadge').style.display = 'block';
            }
        } else {
            scoreElement.textContent = Math.round(currentScore);
        }
    }, stepTime);
}

document.addEventListener('DOMContentLoaded', function() {
    if (isNaN(userLat) || isNaN(userLng)) {
        userLat = 40.7128;
        userLng = -74.0060;
        console.log('Использованы тестовые координаты пользователя');
    }

    if (isNaN(correctLat) || isNaN(correctLng)) {
        correctLat = 55.7558;
        correctLng = 37.6173;
        console.log('Использованы тестовые правильные координаты');
    }

    const distance = calculateDistance(userLat, userLng, correctLat, correctLng);
    const score = calculateScore(distance);

    document.getElementById('distanceValue').textContent = formatDistance(distance);
    document.getElementById('userCoords').textContent = `${userLat.toFixed(6)}, ${userLng.toFixed(6)}`;
    document.getElementById('correctCoords').textContent = `${correctLat.toFixed(6)}, ${correctLng.toFixed(6)}`;

    animateScore(score);

    setTimeout(() => {
        const progressPercent = (score / 10000) * 100;
        document.getElementById('progressBar').style.width = `${progressPercent}%`;
    }, 100);

    ymaps.ready(function() {

    }
        const data = JSON.parse(sessionStorage.getItem('finalResults'));
        const results = data.results;
        const correctLat = data.correctLat;
        const correctLng = data.correctLng;

        const correctPlacemark = new ymaps.Placemark([correctLat, correctLng], {
            balloonContent: 'Правильный ответ'
        }, { preset: 'islands#yellowStarIcon' });
        map.geoObjects.add(correctPlacemark);

        Object.values(results).forEach(player => {
            const playerMark = new ymaps.Placemark([player.lat, player.lng], {
                balloonContent: `${player.name}: ${calculateScore(player.dist)} очков`,
                iconCaption: player.name
            }, { preset: 'islands#greenCircleIcon' });

            const line = new ymaps.Polyline(
                [[player.lat, player.lng], [correctLat, correctLng]],
                {}, { strokeColor: '#ffffff', strokeWidth: 2, strokeOpacity: 0.5 }
            );

            map.geoObjects.add(playerMark);
            map.geoObjects.add(line);
        });

        map.setBounds(map.geoObjects.getBounds());
});

document.getElementById('nextRoundBtn').addEventListener('click', function() {
    sessionStorage.removeItem('userLat');
    sessionStorage.removeItem('userLng');
    window.location.href = '/game';
});
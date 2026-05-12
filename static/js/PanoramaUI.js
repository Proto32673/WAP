// Получаем элементы
const menuOverlay = document.getElementById('menuOverlay');
const menuButton = document.getElementById('menuButton');
const answerBtn = document.getElementById('answerBtn');
const resumeBtn = document.getElementById('resumeBtn');
const restartBtn = document.getElementById('restartBtn');
const exitBtn = document.getElementById('exitBtn');

// Переменная для хранения текущей локации
let currentLocation = null;

// Функция открытия меню
function openMenu() {
    menuOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
}

// Функция закрытия меню
function closeMenu() {
    menuOverlay.classList.remove('active');
    document.body.style.overflow = '';
}

// Обработчик нажатия ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape' || event.key === 'Esc') {
        if (menuOverlay.classList.contains('active')) {
            closeMenu();
        } else {
            openMenu();
        }
    }
});

// Кнопка меню (три полоски)
menuButton.addEventListener('click', openMenu);

// Продолжить игру - закрыть меню
resumeBtn.addEventListener('click', closeMenu);

// Начать заново - перезагрузить страницу
restartBtn.addEventListener('click', function() {
    if (confirm('Вы уверены, что хотите начать игру заново? Прогресс будет потерян.')) {
        location.reload();
    }
});

// Выйти в меню - на главную
exitBtn.addEventListener('click', function() {
    if (confirm('Вы уверены, что хотите выйти в главное меню?')) {
        window.location.href = '/';
    }
});

answerBtn.addEventListener('click', function() {
    if (confirm('Вы уверены, что хотите ответить?')) {
        if (window.currentLocation) {
            const lat = window.currentLocation.lat;
            const lng = window.currentLocation.lng;
            const name = window.currentLocation.name || "Неизвестное место";
            const roundId = window.currentLocation.id || Date.now();
            if(ROOM_CODE){
                window.location.replace(`/map?lat=${lat}&lng=${lng}&name=${encodeURIComponent(name)}&round_id=${roundId}&code=${ROOM_CODE}`)
            }
            else{
                window.location.replace(`/map?lat=${lat}&lng=${lng}&name=${encodeURIComponent(name)}&round_id=${roundId}`)
            }
        }
        else {
            alert('Подождите загрузки панорамы...');
        }
    }
});

// Закрытие меню при клике на оверлей
menuOverlay.addEventListener('click', function(event) {
    if (event.target === menuOverlay) {
        closeMenu();
    }
});
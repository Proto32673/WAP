document.addEventListener('DOMContentLoaded', () => {
    const html = document.documentElement;
    const switcher = document.getElementById('themeSwitcher');
    const updateIcon = (theme) => {
        switcher.innerHTML = theme === 'dark' ? '☀️' : '🌙';
    };

    // 1. Проверка при загрузке
    const savedTheme = localStorage.getItem('theme') || 'light';
    html.setAttribute('data-bs-theme', savedTheme);
    updateIcon(savedTheme);

    // 2. Клик по кнопке
    switcher.addEventListener('click', () => {
        const currentTheme = html.getAttribute('data-bs-theme');
        const newTheme = currentTheme === 'light' ? 'dark' : 'light';

        html.setAttribute('data-bs-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        updateIcon(newTheme);
    });
});
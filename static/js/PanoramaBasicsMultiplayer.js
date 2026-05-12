document.addEventListener('DOMContentLoaded', () => {
    window.socket = io();

    socket.on('connect', () => {
        socket.emit('join', { room: ROOM_CODE });
    });
    ymaps.ready(() => {
        if (!ymaps.panorama.isSupported()) return;
        window.currentLocation = null;
        const cleanPanorama = (panorama) => {
            panorama.getMarkers = () => [];


            panorama.getConnectionMarkers = () => [];
            if (panorama.getGraph) panorama.getGraph = () => null;

            return panorama;
        };
        window.put_pano_in_player = (panorama) => {
            const cleanedPano = cleanPanorama(panorama);
            if (window.player) {
                window.player.setPanorama(cleanedPano);

                window.player.setDirection([Math.random() * 360, 0]);

            } else {
                window.player = new ymaps.panorama.Player('player1', cleanedPano, {
                    direction: [Math.random() * 360, 0],
                    span: [80, 80],
                    controls: [],

                    suppressMapOpenBlock: true
                });
            }
        };

        if (IS_CREATOR) {
            window.findWorldPano = (attempts) => {

                if (attempts <= 0) {
                    return;
                }


                fetch('/api/location')
                    .then(res => res.json())

                    .then(data => {

                        ymaps.panorama.locate([data.lat, data.lng]).done((panoramas) => {
                            if (panoramas.length > 0) {
                                window.currentLocation = data;
                                put_pano_in_player(panoramas[0]);

                                socket.emit('player_move', {
                                    room: ROOM_CODE,
                                    lat: data.lat,
                                    lng: data.lng,
                                    name: data.name,
                                    id: data.id
                                });
                            } else {
                                findWorldPano(attempts - 1);
                            }
                        });
                    })
                    .catch(() => findWorldPano(attempts - 1));
            };
            findWorldPano(7);
        }
        socket.on('update', (data) => {
            window.currentLocation = data;

            sessionStorage.setItem('correctLat', data.lat);
            sessionStorage.setItem('correctLng', data.lng);
            ymaps.panorama.locate([data.lat, data.lng]).done((panoramas) => {
                if (panoramas.length > 0) {

                    put_pano_in_player(panoramas[0]);
                }
            });
        });
    });
});
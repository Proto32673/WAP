ymaps.ready(function () {
    if (!ymaps.panorama.isSupported()) return;
    window.findWorldPano = function(attempts) {
        if (attempts <= 0) return;
        fetch('/api/get_location')
            .then(response => response.json())
            .then(coords => {
                ymaps.panorama.locate([coords.lat, coords.lng]).done(function (panoramas) {
                    if (panoramas.length > 0) {
                        var panorama = panoramas[0];
                        var proto = Object.getPrototypeOf(panorama);
                        proto.getMarkers = function () { return []; };
                        proto.getConnectionMarkers = function () { return []; };

                        put_pano_in_player(panorama);
                    } else {
                        findWorldPano(attempts - 1);
                    }
                });
            });
    }
    window.put_pano_in_player = function (panorama) {
        if (window.player) {
            window.player.setPanorama(panorama);
            window.player.setDirection([Math.random() * 360, 0]);
        } else {
            window.player = new ymaps.panorama.Player(
                'player1',
                panorama,
                {
                    direction: [Math.random() * 360, 0],
                    span: [80, 80],
                    controls: [],
                    suppressMapOpenBlock: true
                }
            );
        }
    }
    findWorldPano(5);
});
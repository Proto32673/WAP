ymaps.ready(function () {
    if (!ymaps.panorama.isSupported()) return;

    window.get_ypano = function (x, y) {
        ymaps.panorama.locate([y, x]).done(
            function (pano_list) {
                if (pano_list.length > 0) {
                    var panorama = pano_list[0];
                    var proto = Object.getPrototypeOf(panorama);
                    proto.getMarkers = function () { return []; };
                    proto.getConnectionMarkers = function () { return []; };
                    put_pano_in_player(panorama);
                } else {
                    console.log('no pano here');
                }
            }
        );
    }

    window.put_pano_in_player = function (panorama) {
        if (window.player) {
            window.player.setPanorama(panorama);
        } else {
            window.player = new ymaps.panorama.Player(
                'player1',
                panorama,
                {
                    direction: [0, 0],
                    span: [80, 80],
                    controls: 'zoomControl'
                }
            );

            window.player.events.add(['directionchange', 'spanchange'], function () {
                if (typeof get_hs === "function") get_hs(window.player);
            });
        }
        $('[class*=panorama-control]').css({"display": "none"});
    }
    get_ypano(37.588264, 55.733685);
});
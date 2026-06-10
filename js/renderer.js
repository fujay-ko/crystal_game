window.Game = window.Game || {};

(function(G) {

var C = G.CONST;
var L = G.LAYOUT;
var mapData = G.MAP_DATA;

G.drawGame = function(overrideMsg) {
    var canvas = document.getElementById('gameCanvas');
    var ctx = canvas.getContext('2d');
    var d = G.getD();
    var tile = C.TILE_SIZE;

    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // 1. Background
    var bg = G.getImage('bg');
    if (bg) ctx.drawImage(bg, 0, 0);

    // 2. Map tiles
    for (var r = 0; r < 8; r++) {
        for (var c = 0; c < 8; c++) {
            var x = c * tile;
            var y = r * tile;
            if (mapData[r][c] === 0) {
                var wall = G.getImage('wall');
                if (wall) ctx.drawImage(wall, x, y);
            } else {
                var road = G.getImage('road');
                if (road) ctx.drawImage(road, x, y);
            }
        }
    }

    // 3. Crystals on map
    d.crystals_on_map.forEach(function(crystal) {
        var img = G.getImage(crystal.colorKey);
        if (img) ctx.drawImage(img, crystal.col * tile, crystal.row * tile);
    });

    // 4. Character
    var mcKey = 'mc' + d.dir;
    var arrowKey = 'arrow' + d.dir;
    var mcImg = G.getImage(mcKey);
    if (mcImg) ctx.drawImage(mcImg, d.col * tile, d.row * tile);

    var ax = d.col * tile, ay = d.row * tile;
    switch (d.dir) {
        case 0: ax += 16; ay = (d.row - 1) * tile + 48; break;
        case 1: ax = (d.col + 1) * tile - 16; ay += 16; break;
        case 2: ax += 16; ay = (d.row + 1) * tile - 16; break;
        case 3: ax = (d.col - 1) * tile + 48; ay += 16; break;
    }
    var arrowImg = G.getImage(arrowKey);
    if (arrowImg) ctx.drawImage(arrowImg, ax, ay);

    // 5. Backpack
    ctx.fillStyle = 'black';
    ctx.font = "20px 'Comic Sans MS', Arial";
    ctx.textAlign = 'center';
    ctx.fillText(d.crystals_collected + ' / 5', L.BACKPACK_TEXT.x, L.BACKPACK_TEXT.y);

    for (var i = 0; i < 5; i++) {
        var boxImg = G.getImage('box');
        if (boxImg) ctx.drawImage(boxImg, L.BACKPACK_START.x + i * L.BACKPACK_SLOT_SIZE, L.BACKPACK_START.y);
        if (i < d.crystals_collected) {
            var cKey = G.CRYSTAL_CONFIG[i] ? G.CRYSTAL_CONFIG[i].colorKey : ('c' + (i + 1));
            var cImg = G.getImage(cKey);
            if (cImg) ctx.drawImage(cImg,
                L.BACKPACK_START.x + L.BACKPACK_ICON_OFFSET + i * L.BACKPACK_SLOT_SIZE,
                L.BACKPACK_START.y + L.BACKPACK_ICON_OFFSET,
                L.BACKPACK_ICON_SIZE, L.BACKPACK_ICON_SIZE);
        }
    }

    // 6. Function panel
    var funcImg = G.getImage('func');
    if (funcImg) ctx.drawImage(funcImg, L.FUNC_PANEL.x, L.FUNC_PANEL.y);

    // 7. Mission scroll
    var stage = d.crystals_collected + 1;
    if (stage > 5) stage = 5;
    var mImg = G.getImage('m' + stage);
    if (mImg) ctx.drawImage(mImg, L.SCROLL.x, L.SCROLL.y);

    // 8. Bottom progress bar
    ctx.font = "20px 'Comic Sans MS', Arial";
    ctx.fillText('Mission: Get Crystals', L.PROGRESS_TITLE.x, L.PROGRESS_TITLE.y);

    L.STAGE_LABELS.forEach(function(label) {
        ctx.fillText(label.text, label.x, label.y);
        var iconImg = G.getImage(label.icon);
        if (iconImg) ctx.drawImage(iconImg, label.iconX, label.iconY);
    });

    // 9. Victory / Defeat overlay
    if (overrideMsg === 'victory') {
        var vicImg = G.getImage('victory');
        if (vicImg) ctx.drawImage(vicImg, L.VICTORY_IMG.x, L.VICTORY_IMG.y);
    }
    if (overrideMsg === 'defeat') {
        var defImg = G.getImage('defeat');
        if (defImg) ctx.drawImage(defImg, L.DEFEAT_IMG.x, L.DEFEAT_IMG.y);
    }
};

})(window.Game);

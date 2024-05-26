importPackage(java.awt);
importPackage(java.awt.geom);
include(Resources.id('mtrsteamloco:scripts/display_helper.js'));

let slotCfg = {
    version: 1,
    texSize: [1024, 128],
    slots: [
        {
            name: 'head',
            texArea: [0, 0, 1024, 128],
            pos: [
                [
                    [-0.723, 2.165, 7.02],
                    [-0.723, 1.98, 7.02],
                    [0.7, 1.98, 7.02],
                    [0.7, 2.165, 7.02],
                ],
            ],
            offsets: [[0, 0, 0]],
        },
    ],
};

let slotReversedCfg = {
    version: 1,
    texSize: [1024, 128],
    slots: [
        {
            name: 'head-reversed',
            texArea: [0, 0, 1024, 128],
            pos: [
                [
                    [0.723, 2.165, -7.02],
                    [0.723, 1.98, -7.02],
                    [-0.7, 1.98, -7.02],
                    [-0.7, 2.165, -7.02],
                ],
            ],
            offsets: [[0, 0, 0]],
        },
    ],
};

let dhBase = new DisplayHelper(slotCfg);
let dhReversedBase = new DisplayHelper(slotReversedCfg);

function create(ctx, state, train) {
    state.pisRateLimit = new RateLimit(0.05);
    state.dh = dhBase.create();
    state.dhReversed = dhReversedBase.create();
    state.routeID = Math.floor(Math.random() * 100);
}

function dispose(ctx, state, train) {
    state.dh.close();
    state.dhReversed.close();
}

var EMUFont = Resources.readFont(
    Resources.idRelative('mtr:metropack/fonts/81-740-metro-train.ttf')
);

function render(ctx, state, train) {
    if (state.pisRateLimit.shouldUpdate()) {
        let g;

        let EMUText = getDestinationStation(train);

        [
            { dh: state.dh, graphicsName: 'head' },
            { dh: state.dhReversed, graphicsName: 'head-reversed' },
        ].forEach((element) => {
            let dh = element.dh;
            g = dh.graphicsFor(element.graphicsName);
            g.setColor(Color.BLACK);
            g.fillRect(0, 0, 1024, 128);
            g.setColor(Color.GREEN);
            g.setFont(EMUFont.deriveFont(Font.PLAIN, 32));
            g.drawString(state.routeID, 0, 128);
            let fontMetrics = g.getFontMetrics();
            let routeWidth = fontMetrics.stringWidth(state.routeID);
            let textWidth = fontMetrics.stringWidth(EMUText);
            g.drawString(
                EMUText,
                routeWidth + (1024 - routeWidth - textWidth) / 2,
                128
            );
            dh.upload();
        });
    }

    ctx.drawCarModel(state.dh.model, 0, null);
    ctx.drawCarModel(state.dhReversed.model, train.trainCars() - 1, null);
}

function getDestinationStation(train) {
    let stationList = train.getThisRoutePlatforms();
    let lastPlatform = stationList[stationList.size() - 1];
    if (lastPlatform === undefined) return 'ПОСАДКИ НЕТ';
    return lastPlatform.destinationName.split('\\|')[0].toUpperCase();
}

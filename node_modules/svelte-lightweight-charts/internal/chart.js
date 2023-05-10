import { createChart } from 'lightweight-charts';
export function chart(node, params) {
    var _a, _b;
    let { options, reference, onClick, onCrosshairMove, } = params;
    let width = (_a = options === null || options === void 0 ? void 0 : options.width) !== null && _a !== void 0 ? _a : 0;
    let height = (_b = options === null || options === void 0 ? void 0 : options.height) !== null && _b !== void 0 ? _b : 0;
    const chart = createChart(node, options);
    reference === null || reference === void 0 ? void 0 : reference(chart);
    if (onClick) {
        chart.subscribeClick(onClick);
    }
    if (onCrosshairMove) {
        chart.subscribeCrosshairMove(onCrosshairMove);
    }
    return {
        update(nextParams) {
            var _a, _b;
            const { options: nextOptions, reference: nextReference, onClick: nextOnClick, onCrosshairMove: nextOnCrosshairMove, } = nextParams;
            if (nextReference !== reference) {
                reference === null || reference === void 0 ? void 0 : reference(null);
                reference = nextReference;
                reference === null || reference === void 0 ? void 0 : reference(chart);
            }
            if (nextOptions) {
                chart.applyOptions(nextOptions);
                if (nextOptions.width !== undefined && nextOptions.width !== width
                    || nextOptions.height !== undefined && nextOptions.height !== height) {
                    width = (_a = nextOptions.width) !== null && _a !== void 0 ? _a : width;
                    height = (_b = nextOptions.height) !== null && _b !== void 0 ? _b : height;
                    chart.resize(width, height, true);
                }
                options = nextOptions;
            }
            if (nextOnClick !== onClick) {
                if (onClick) {
                    chart.unsubscribeClick(onClick);
                }
                onClick = nextOnClick;
                if (onClick) {
                    chart.subscribeClick(onClick);
                }
            }
            if (nextOnCrosshairMove !== onCrosshairMove) {
                if (onCrosshairMove) {
                    chart.unsubscribeCrosshairMove(onCrosshairMove);
                }
                onCrosshairMove = nextOnCrosshairMove;
                if (onCrosshairMove) {
                    chart.subscribeCrosshairMove(onCrosshairMove);
                }
            }
        },
        destroy() {
            if (onClick) {
                chart.unsubscribeClick(onClick);
            }
            if (onCrosshairMove) {
                chart.unsubscribeCrosshairMove(onCrosshairMove);
            }
            chart.remove();
            reference === null || reference === void 0 ? void 0 : reference(null);
        }
    };
}

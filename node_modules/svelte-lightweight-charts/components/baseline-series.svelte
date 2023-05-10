<svelte:options immutable={true}/>

<script >import ContextProvider from './internal/context-provider.svelte';
import { useSeriesEffect } from './internal/utils.js';
/** Visibility of the label with the latest visible price on the price scale */
export let lastValueVisible = undefined;
/** Title of the series. This label is placed with price axis label */
export let title = undefined;
/** Target price scale to bind new series to */
export let priceScaleId = undefined;
/** Visibility of series. */
export let visible = undefined;
/** Visibility of the price line. Price line is a horizontal line indicating the last price of the series */
export let priceLineVisible = undefined;
/** Enum of possible modes of priceLine source */
export let priceLineSource = undefined;
/** Width of the price line. Ignored if priceLineVisible is false */
export let priceLineWidth = undefined;
/** Color of the price line. Ignored if priceLineVisible is false */
export let priceLineColor = undefined;
/** Price line style. Suitable for percentage and indexedTo100 scales */
export let priceLineStyle = undefined;
/** Formatting settings associated with the series */
export let priceFormat = undefined;
/** Visibility of base line. Suitable for percentage and indexedTo100 scales */
export let baseLineVisible = undefined;
/** Color of the base line in IndexedTo100 mode */
export let baseLineColor = undefined;
/** Base line width. Suitable for percentage and indexedTo100 scales. Ignored if baseLineVisible is not set */
export let baseLineWidth = undefined;
/** Base line style. Suitable for percentage and indexedTo100 scales. Ignored if baseLineVisible is not set */
export let baseLineStyle = undefined;
/** function that overrides calculating of visible prices range */
export let autoscaleInfoProvider = undefined;
/**
 * Base value of the series.
 */
export let baseValue = undefined;
/**
 * The first color of the top area.
 */
export let topFillColor1 = undefined;
/**
 * The second color of the top area.
 */
export let topFillColor2 = undefined;
/**
 * The line color of the top area.
 */
export let topLineColor = undefined;
/**
 * The first color of the bottom area.
 */
export let bottomFillColor1 = undefined;
/**
 * The second color of the bottom area.
 */
export let bottomFillColor2 = undefined;
/**
 * The line color of the bottom area.
 */
export let bottomLineColor = undefined;
/**
 * Line width.
 */
export let lineWidth = undefined;
/**
 * Line style.
 */
export let lineStyle = undefined;
/**
 * Show the crosshair marker.
 */
export let crosshairMarkerVisible = undefined;
/**
 * Crosshair marker radius in pixels.
 */
export let crosshairMarkerRadius = undefined;
/**
 * Crosshair marker border color. An empty string falls back to the the color of the series under the crosshair.
 */
export let crosshairMarkerBorderColor = undefined;
/**
 * The crosshair marker background color. An empty string falls back to the the color of the series under the crosshair.
 */
export let crosshairMarkerBackgroundColor = undefined;
/**
 * Last price animation mode.
 */
export let lastPriceAnimation = undefined;
export let ref = undefined;
export let data = [];
export let reactive = false;
export let markers = [];
let options;
$: options = {
    lastValueVisible,
    title,
    priceScaleId,
    visible,
    priceLineVisible,
    priceLineSource,
    priceLineWidth,
    priceLineColor,
    priceLineStyle,
    priceFormat,
    baseLineVisible,
    baseLineColor,
    baseLineWidth,
    baseLineStyle,
    autoscaleInfoProvider,
    baseValue,
    topFillColor1,
    topFillColor2,
    topLineColor,
    bottomFillColor1,
    bottomFillColor2,
    bottomLineColor,
    lineStyle,
    lineWidth,
    crosshairMarkerBackgroundColor,
    crosshairMarkerBorderColor,
    crosshairMarkerRadius,
    crosshairMarkerVisible,
    lastPriceAnimation,
};
let reference = null;
let handleReference = undefined;
$: handleReference = ((ref) => (series) => {
    reference = series;
    if (ref !== undefined) {
        ref(series);
    }
})(ref);
const id = performance.now().toString();
useSeriesEffect(() => [
    {
        id,
        type: 'Baseline',
        reactive,
        options,
        data,
        markers,
    },
    handleReference,
]);
</script>
{#if reference !== null}
    <ContextProvider value={reference}>
        <slot/>
    </ContextProvider>
{/if}

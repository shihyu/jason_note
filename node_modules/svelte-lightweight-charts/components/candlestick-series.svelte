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
/** Color of rising candlesticks */
export let upColor = undefined;
/** Color of falling candlesticks */
export let downColor = undefined;
/** Flag to draw/hide candlestick wicks */
export let wickVisible = undefined;
/** Flag to draw/hide candlestick borders around bodies */
export let borderVisible = undefined;
/**
 * Color of borders around candles' bodies. Ignored if borderVisible == false
 * If specified, it overrides both borderUpColor and borderDownColor options
 */
export let borderColor = undefined;
/** Color of the border of rising candlesticks. Ignored if borderVisible == false or borderColor is specified */
export let borderUpColor = undefined;
/** Color of the border of rising candlesticks. Ignored if borderVisible == false or borderColor is specified */
export let borderDownColor = undefined;
/**
 * Color of candlestick wicks. Ignored if wickVisible == false
 * If specified, it overrides both wickUpColor and wickDownColor options
 */
export let wickColor = undefined;
/** Color of rising candlestick wicks. Ignored if wickVisible == false or wickColor is specified */
export let wickUpColor = undefined;
/** Color of falling candlestick wicks. Ignored if wickVisible == false or wickColor is specified */
export let wickDownColor = undefined;
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
    upColor,
    downColor,
    wickColor,
    borderColor,
    borderUpColor,
    borderDownColor,
    wickVisible,
    borderVisible,
    wickUpColor,
    wickDownColor,
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
        type: 'Candlestick',
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

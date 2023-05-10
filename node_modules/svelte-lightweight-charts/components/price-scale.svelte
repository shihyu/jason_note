<svelte:options immutable={true}/>

<script >import { usePriceScaleEffect } from './internal/utils.js';
export let id;
/**
 * Automatically set price range based on visible data range.
 */
export let autoScale = undefined;
/** Price scale mode. */
export let mode = undefined;
/**
 * Invert the price scale, so that a upwards trend is shown as a downwards trend and vice versa.
 * Affects both the price scale and the data on the chart.
 */
export let invertScale = undefined;
/**
 * Align price scale labels to prevent them from overlapping.
 */
export let alignLabels = undefined;
/**
 * Price scale margins.
 */
export let scaleMargins = undefined;
/**
 * Set true to draw a border between the price scale and the chart area.
 */
export let borderVisible = undefined;
/**
 * Price scale border color.
 */
export let borderColor = undefined;
/**
 * Price scale text color.
 * If not provided {@link LayoutOptions.textColor} is used.
 */
export let textColor = undefined;
/**
 * Show top and bottom corner labels only if entire text is visible.
 */
export let entireTextOnly = undefined;
/** Indicates if this price scale visible. Ignored by overlay price scales. */
export let visible = undefined;
/** Draw small horizontal line on price axis labels. */
export let ticksVisible = undefined;
export let ref = undefined;
let options = {
    autoScale,
    mode,
    invertScale,
    alignLabels,
    scaleMargins,
    borderVisible,
    borderColor,
    textColor,
    entireTextOnly,
    visible,
    ticksVisible,
};
$: options = {
    autoScale,
    mode,
    invertScale,
    alignLabels,
    scaleMargins,
    borderVisible,
    borderColor,
    textColor,
    entireTextOnly,
    visible,
    ticksVisible,
};
usePriceScaleEffect(() => [
    {
        id,
        options,
    },
    ref
]);
</script>

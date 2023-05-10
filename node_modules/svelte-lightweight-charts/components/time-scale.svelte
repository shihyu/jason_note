<svelte:options immutable={true}/>

<script >import { createEventDispatcher } from 'svelte';
import { useTimeScaleEffect } from './internal/utils.js';
const dispatch = createEventDispatcher();
/**
 * The margin space in bars from the right side of the chart.
 */
export let rightOffset = undefined;
/**
 * The space between bars in pixels.
 */
export let barSpacing = undefined;
/**
 * The minimum space between bars in pixels.
 */
export let minBarSpacing = undefined;
/**
 * Prevent scrolling to the left of the first bar.
 */
export let fixLeftEdge = undefined;
/**
 * Prevent scrolling to the right of the most recent bar.
 */
export let fixRightEdge = undefined;
/**
 * Prevent changing the visible time range during chart resizing.
 */
export let lockVisibleTimeRangeOnResize = undefined;
/**
 * Prevent the hovered bar from moving when scrolling.
 */
export let rightBarStaysOnScroll = undefined;
/**
 * Show the time scale border.
 */
export let borderVisible = undefined;
/**
 * The time scale border color.
 */
export let borderColor = undefined;
/**
 * Show the time scale.
 */
export let visible = undefined;
/**
 * Show the time, not just the date, in the time scale and vertical crosshair label.
 */
export let timeVisible = undefined;
/**
 * Show seconds in the time scale and vertical crosshair label in `hh:mm:ss` format for intraday data.
 */
export let secondsVisible = undefined;
/**
 * Shift the visible range to the right (into the future) by the number of new bars when new data is added.
 *
 * Note that this only applies when the last bar is visible.
 */
export let shiftVisibleRangeOnNewBar = undefined;
/**
 * Override the default tick marks formatter.
 */
export let tickMarkFormatter = undefined;
export let ref = undefined;
let options = {
    rightOffset,
    barSpacing,
    minBarSpacing,
    fixLeftEdge,
    fixRightEdge,
    lockVisibleTimeRangeOnResize,
    rightBarStaysOnScroll,
    borderVisible,
    borderColor,
    visible,
    timeVisible,
    secondsVisible,
    shiftVisibleRangeOnNewBar,
    tickMarkFormatter,
};
$: options = {
    rightOffset,
    barSpacing,
    minBarSpacing,
    fixLeftEdge,
    fixRightEdge,
    lockVisibleTimeRangeOnResize,
    rightBarStaysOnScroll,
    borderVisible,
    borderColor,
    visible,
    timeVisible,
    secondsVisible,
    shiftVisibleRangeOnNewBar,
    tickMarkFormatter,
};
function handleVisibleTimeRangeChange(timeRange) {
    dispatch('visibleTimeRangeChange', timeRange);
}
function handleVisibleLogicalRangeChange(logicalRange) {
    dispatch('visibleLogicalRangeChange', logicalRange);
}
function handleSizeChange(width, height) {
    dispatch('sizeChange', { width, height });
}
useTimeScaleEffect(() => [
    {
        options,
        onVisibleTimeRangeChange: handleVisibleTimeRangeChange,
        onVisibleLogicalRangeChange: handleVisibleLogicalRangeChange,
        onSizeChange: handleSizeChange,
    },
    ref
]);
</script>

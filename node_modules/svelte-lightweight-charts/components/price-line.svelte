<svelte:options immutable={true}/>

<script >import { useLineEffect } from './internal/utils.js';
export let price;
export let color;
export let lineWidth;
export let lineStyle;
export let axisLabelVisible;
export let title;
export let ref = undefined;
let options = {
    price,
    color,
    lineWidth,
    lineStyle,
    axisLabelVisible,
    title,
};
$: options = {
    price,
    color,
    lineWidth,
    lineStyle,
    axisLabelVisible,
    title,
};
const id = performance.now().toString();
useLineEffect(() => [
    {
        id,
        options,
    },
    ref
]);
</script>

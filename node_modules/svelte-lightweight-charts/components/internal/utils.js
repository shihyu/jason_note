import { afterUpdate, getContext, onMount, setContext } from 'svelte';
import { series } from '../../internal/series.js';
import { line } from '../../internal/lines.js';
import { timeScale } from '../../internal/time-scale.js';
import { priceScale } from '../../internal/price-scale.js';
export function context(value) {
    if (typeof value !== 'undefined') {
        setContext('lightweight-chart-context', value);
    }
    else {
        return getContext('lightweight-chart-context');
    }
}
export function useSeriesEffect(callback) {
    let subject = null;
    const api = context();
    onMount(() => {
        const [params] = callback();
        subject = series(api, params);
        return () => {
            subject === null || subject === void 0 ? void 0 : subject.destroy();
            subject = null;
        };
    });
    afterUpdate(() => {
        const [params, ref] = callback();
        subject === null || subject === void 0 ? void 0 : subject.update(params);
        subject === null || subject === void 0 ? void 0 : subject.updateReference(ref);
    });
}
export function useLineEffect(callback) {
    let subject = null;
    const api = context();
    onMount(() => {
        const [params] = callback();
        subject = line(api, params);
        return () => {
            subject === null || subject === void 0 ? void 0 : subject.destroy();
            subject = null;
        };
    });
    afterUpdate(() => {
        const [params, ref] = callback();
        subject === null || subject === void 0 ? void 0 : subject.update(params);
        subject === null || subject === void 0 ? void 0 : subject.updateReference(ref);
    });
}
export function useTimeScaleEffect(callback) {
    let subject = null;
    const api = context();
    onMount(() => {
        const [params] = callback();
        subject = timeScale(api, params);
        return () => {
            subject === null || subject === void 0 ? void 0 : subject.destroy();
            subject = null;
        };
    });
    afterUpdate(() => {
        const [params, ref] = callback();
        subject === null || subject === void 0 ? void 0 : subject.update(params);
        subject === null || subject === void 0 ? void 0 : subject.updateReference(ref);
    });
}
export function usePriceScaleEffect(callback) {
    let subject = null;
    const api = context();
    onMount(() => {
        const [params] = callback();
        subject = priceScale(api, params);
        return () => {
            subject === null || subject === void 0 ? void 0 : subject.destroy();
            subject = null;
        };
    });
    afterUpdate(() => {
        const [params, ref] = callback();
        subject === null || subject === void 0 ? void 0 : subject.update(params);
        subject === null || subject === void 0 ? void 0 : subject.updateReference(ref);
    });
}

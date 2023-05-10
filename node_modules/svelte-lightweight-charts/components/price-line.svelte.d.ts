import { SvelteComponentTyped } from 'svelte';
import type {IPriceLine, CreatePriceLineOptions} from 'lightweight-charts';
import type {Reference} from '../internal/utils.js';

export interface $$PROPS extends CreatePriceLineOptions {
    ref?: Reference<IPriceLine>;
}

// eslint-disable-next-line @typescript-eslint/no-empty-interface
export interface $$EVENTS {

}

export default class PriceLine extends SvelteComponentTyped<$$PROPS, $$EVENTS> {}
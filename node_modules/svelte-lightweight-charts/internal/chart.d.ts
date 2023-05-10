import type { ChartOptions, DeepPartial, IChartApi, MouseEventHandler } from 'lightweight-charts';
import type { ActionResult, Reference } from './utils.js';
export interface ChartActionParams {
    options?: DeepPartial<ChartOptions>;
    reference?: Reference<IChartApi>;
    onClick?: MouseEventHandler;
    onCrosshairMove?: MouseEventHandler;
}
export declare function chart(node: HTMLElement, params: ChartActionParams): ActionResult<ChartActionParams>;

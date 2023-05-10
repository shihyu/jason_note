import type { IChartApi, IPriceScaleApi, DeepPartial, PriceScaleOptions } from 'lightweight-charts';
import type { ReferencableActionResult, Reference } from './utils.js';
export interface PriceScaleParams {
    id: string;
    options?: DeepPartial<PriceScaleOptions>;
    reference?: Reference<IPriceScaleApi>;
}
export type PriceScaleActionResult = ReferencableActionResult<PriceScaleParams, IPriceScaleApi>;
export declare function priceScale(target: IChartApi, params: PriceScaleParams): PriceScaleActionResult;

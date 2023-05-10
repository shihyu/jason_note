import type { IPriceLine, ISeriesApi, SeriesType, CreatePriceLineOptions } from 'lightweight-charts';
import type { ReferencableActionResult, Reference } from './utils.js';
export interface PriceLineParams {
    id: string;
    options: CreatePriceLineOptions;
    reference?: Reference<IPriceLine>;
}
export type PriceLineActionResult = ReferencableActionResult<PriceLineParams, IPriceLine>;
export declare function line<T extends SeriesType>(target: ISeriesApi<T>, params: PriceLineParams): PriceLineActionResult;

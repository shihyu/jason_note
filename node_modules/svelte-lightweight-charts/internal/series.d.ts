import type { IChartApi, ISeriesApi, SeriesType, SeriesDataItemTypeMap, SeriesPartialOptionsMap, SeriesMarker, Time } from 'lightweight-charts';
import type { ReferencableActionResult, Reference } from './utils.js';
export interface AreaSeriesParams {
    id: string;
    type: 'Area';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Area'];
    data: SeriesDataItemTypeMap['Area'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Area'>>;
}
export interface BarSeriesParams {
    id: string;
    type: 'Bar';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Bar'];
    data: SeriesDataItemTypeMap['Bar'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Bar'>>;
}
export interface CandlestickSeriesParams {
    id: string;
    type: 'Candlestick';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Candlestick'];
    data: SeriesDataItemTypeMap['Candlestick'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Candlestick'>>;
}
export interface HistogramSeriesParams {
    id: string;
    type: 'Histogram';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Histogram'];
    data: SeriesDataItemTypeMap['Histogram'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Histogram'>>;
}
export interface LineSeriesParams {
    id: string;
    type: 'Line';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Line'];
    data: SeriesDataItemTypeMap['Line'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Line'>>;
}
export type BaselineSeriesParams = 'Baseline' extends SeriesType ? {
    id: string;
    type: 'Baseline';
    reactive?: boolean;
    options?: SeriesPartialOptionsMap['Baseline'];
    data: SeriesDataItemTypeMap['Baseline'][];
    markers: SeriesMarker<Time>[];
    reference?: Reference<ISeriesApi<'Baseline'>>;
} : never;
export type SeriesActionParams = AreaSeriesParams | BarSeriesParams | CandlestickSeriesParams | HistogramSeriesParams | LineSeriesParams | BaselineSeriesParams;
export type SeriesParams = Omit<SeriesActionParams, 'reference'>;
export type SeriesActionResult<T extends SeriesParams> = ReferencableActionResult<T, ISeriesApi<T['type']>>;
export declare function series<T extends SeriesParams>(target: IChartApi, params: T): SeriesActionResult<T>;

import type { IChartApi, ITimeScaleApi, DeepPartial, LogicalRangeChangeEventHandler, SizeChangeEventHandler, TimeRangeChangeEventHandler, TimeScaleOptions } from 'lightweight-charts';
import type { ReferencableActionResult, Reference } from './utils.js';
export interface TimeScaleParams {
    options?: DeepPartial<TimeScaleOptions>;
    reference?: Reference<ITimeScaleApi>;
    onVisibleTimeRangeChange?: TimeRangeChangeEventHandler;
    onVisibleLogicalRangeChange?: LogicalRangeChangeEventHandler;
    onSizeChange?: SizeChangeEventHandler;
}
export type TimeScaleActionResult = ReferencableActionResult<TimeScaleParams, ITimeScaleApi>;
export declare function timeScale(target: IChartApi, params: TimeScaleParams): TimeScaleActionResult;

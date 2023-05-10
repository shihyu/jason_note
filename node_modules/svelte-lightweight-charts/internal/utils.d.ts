export declare function ensure<T>(value: T | null | undefined): T;
export interface ActionResult<T> {
    update(params: T): void;
    destroy(): void;
}
export type Reference<T> = (ref: T | null) => void;
export interface ReferencableActionResult<P, R> extends ActionResult<P> {
    updateReference(nextReference?: Reference<R>): void;
}
export type Action<TTarget extends Element, TParams> = (target: TTarget, params: TParams) => ActionResult<TParams>;

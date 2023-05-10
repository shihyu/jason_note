export function line(target, params) {
    const subject = target.createPriceLine(params.options);
    let reference;
    return {
        update(nextParams) {
            if (nextParams.options) {
                subject.applyOptions(nextParams.options);
            }
        },
        updateReference(nextReference) {
            if (nextReference !== reference) {
                reference === null || reference === void 0 ? void 0 : reference(null);
                reference = nextReference;
                reference === null || reference === void 0 ? void 0 : reference(subject);
            }
        },
        destroy() {
            reference === null || reference === void 0 ? void 0 : reference(null);
            target.removePriceLine(subject);
        }
    };
}

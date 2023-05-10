export function priceScale(target, params) {
    let { id, options, } = params;
    let subject = target.priceScale(id);
    let reference;
    if (options) {
        subject.applyOptions(options);
    }
    return {
        update(nextParams) {
            const { id: nextId, options: nextOptions, } = nextParams;
            if (nextId !== id) {
                id = nextId;
                reference === null || reference === void 0 ? void 0 : reference(null);
                subject = target.priceScale(id);
                reference === null || reference === void 0 ? void 0 : reference(subject);
            }
            if (nextOptions !== options) {
                options = nextOptions;
                if (options) {
                    subject.applyOptions(options);
                }
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
        }
    };
}

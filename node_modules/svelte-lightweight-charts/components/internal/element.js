export function element(node, reference) {
    let ref = reference;
    ref === null || ref === void 0 ? void 0 : ref(node);
    return {
        update(nextReference) {
            if (nextReference === ref) {
                return;
            }
            ref === null || ref === void 0 ? void 0 : ref(null);
            ref = nextReference;
            ref === null || ref === void 0 ? void 0 : ref(node);
        },
        destroy() {
            ref === null || ref === void 0 ? void 0 : ref(null);
        }
    };
}

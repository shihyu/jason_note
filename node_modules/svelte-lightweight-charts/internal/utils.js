export function ensure(value) {
    if (value === null || value === undefined) {
        throw new Error('no value');
    }
    return value;
}

function isFinite(value){
    let infiniteValues=[NaN, Infinity, -Infinity];
    if (Number(value) in infiniteValues) {
        return false;
    }
    return true;
}
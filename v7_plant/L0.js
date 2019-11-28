console.log("hi");

// set intersection
function intersect(arguments) {
    var output = [];
    var cntObj = {};
    var array, item, cnt;
    // for each array passed as an argument to the function
    for (var i = 0; i < arguments.length; i++) {
        array = arguments[i];
        // for each element in the array
        for (var j = 0; j < array.length; j++) {
            item = "-" + array[j];
            cnt = cntObj[item] || 0;
            // if cnt is exactly the number of previous arrays, 
            // then increment by one so we count only one per array
            if (cnt == i) {
                cntObj[item] = cnt + 1;
            }
        }
    }
    // now collect all results that are in all arrays
    for (item in cntObj) {
        if (cntObj.hasOwnProperty(item) && cntObj[item] === arguments.length) {
            output.push(Number(item.substring(1)));
        }
    }
    return(output);
}


function L0(exs){
    console.log(exs);
    var to_intersect = [];
    Object.entries(exs).forEach(([key, value]) => {
        var exx = value[0] == 2 ? "2" : `(${value[0]}, ${value[1]})`;
        console.log(key);
        var to_qry = `((${key[0]}, ${key[2]}), ${exx})`;
        console.log(l0vs[to_qry]);
        to_intersect.push(l0vs[to_qry]);
    });
    return intersect(to_intersect);
}

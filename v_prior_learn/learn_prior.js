function argMax(array) {
    return array.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
}

let learning_rate = 0.1;
let prior_shape_order = {};

let total_orderings = [];

for (var shapid = 0; shapid < all_shapes.length; shapid++){
    prior_shape_order[shapid] = 1.0;
    total_orderings.push(shapid);
}

// modifys ary in place. be warned.
function swap_order(top_shape_id, other_shape_ids) {
    prior_shape_order[top_shape_id] += learning_rate;
    for (const other_id of other_shape_ids){
        prior_shape_order[other_id] -= learning_rate / other_shape_ids.length;
    }
}

// modifys all_locations in place. be warned
function swap_hard(ords) {
    var all_locations = [];
    for (const ord of ords) {
        all_locations.push(total_orderings.indexOf(ord));
    }
    all_locations.sort(function(a,b) {return a-b});
    //console.log(ords);
    for (var i = 0; i < all_locations.length; i++) {
        let loc = all_locations[i]
        total_orderings[loc] = ords[i];
    }
    //console.log(all_locations);
}

// given a target generate the next_best_s1 utterance
function next_S1_utter(target_id, utters) {
    var new_utrs_scores = S11(target_id, utters);
    var new_utrs = new_utrs_scores[0];
    var new_scores = new_utrs_scores[1];
    var best_id = argMax(new_scores);
    return new_utrs[best_id];
}

function S1_upto(target_id, upto_length) {
    var utters = [];
    for (var i = 0; i < upto_length; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
    }       
    return utters;
}

function sort_prior(N) {
    for (var i = 0; i < N; i++) {
        console.log(i);
        let rand_id = Math.floor(Math.random() * all_shapes.length);
        let rand_n_utts = Math.floor(Math.random() * 3) + 2
        let s1_utts = S1_upto(rand_id, rand_n_utts);
        let l1_ords = Array.from(L1(said_to_dict(s1_utts)));

        swap_hard(l1_ords);
        // let l1_top = l1_ords[0];
        // let l1_rest = l1_ords.slice(1, l1_ords.length);
        // swap_order(l1_top, l1_rest);     
 
    }
}

function download_exp_data(obj){
    var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
    $('<a href="data:' + data + '" download="data.json">download JSON</a>').appendTo('#control');
}

var sample_problems = [17648,13565,7246,10950,14000,8232,2290,5663,1710,10934];
function argMax(array) {
    return array.map((x, i) => [x, i]).reduce((r, a) => (a[0] > r[0] ? a : r))[1];
}

function normalise(list_of_neglogpr) {
    let logprr = list_of_neglogpr.map(x => -x);
    let a = math.max(logprr);
    let yy = logprr.map(x => math.exp(x - a));
    let yy_sum = math.sum(yy);
    let ret = yy.map(y => y / yy_sum);
    return ret
}

var results = [];

// given a target generate the next_best_s1 utterance
function next_S1_utter(target_id, utters) {
    var new_utrs_scores = S11(target_id, utters);
    var new_utrs = new_utrs_scores[0];
    var new_scores = new_utrs_scores[1];
    var best_id = argMax(new_scores);
    return new_utrs[best_id];
}

function S1_L0(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
        let l0_candidates = Array.from(L0(said_to_dict(utters)));
        let subsample_candidates = l0_candidates.sort(function(a,b){
            return random_shape_order[a] - random_shape_order[b];
        });
        if (subsample_candidates[0] == target_id) {
            return [target_id, 'S1', 'L0', utters.length];
        }
    }       
}

function S1_L1(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
        let l1_candidates = Array.from(L1(said_to_dict(utters)));
        if (l1_candidates[0] == target_id) {
            return [target_id, 'S1', 'L1', utters.length];
        }
    }       
}

function S1_Lp(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
        let l1_candidates = Array.from(L_prior(said_to_dict(utters)));
        if (l1_candidates[0] == target_id) {
            return [target_id, 'S1', 'Lp', utters.length];
        }
    }       
}


function S0_L0(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        var new_utrs = S0(target_id, utters);
        const random_utr = new_utrs[Math.floor(Math.random() * new_utrs.length)];
        utters.push(random_utr);
        
        let l0_candidates = Array.from(L0(said_to_dict(utters)));
        let subsample_candidates = l0_candidates.sort(function(a,b){
            return random_shape_order[a] - random_shape_order[b];
        });
        if (subsample_candidates[0] == target_id) {
            return [target_id, 'S0', 'L0', utters.length];
        }
    }
}

function experiment(to_run, n_trials) {
    sample_problems.forEach(x => {
        var rounds = [];
        for (var attempts = 0; attempts < n_trials; attempts++) {
            
            // control randomness here by re-freshing
            L0SETS = {};
            solved_instances = {};
            for (var shapid = 0; shapid < all_shapes.length; shapid++){
                random_shape_order[shapid] = Math.random();
            }

            let round = to_run(x);
            results.push(round);
        }
        console.log("done with ", x);
    });    
}

// make new problem instance
function new_problem_id(new_target_id){
    target_id = new_target_id;
    // grab new target-id and clear examples
    target = all_shapes[target_id];
    examples = {};
    // clear all boxes with empty
    for (var jjj=0; jjj<3; jjj++){
        clear_grid_canvas("#cand_box_"+jjj);
    }
    clear_candidate_border();
    clear_grid_canvas("#box_");
    // re-render target image
    for (var i=0; i<L; i+=1) {
        for (var j=0; j<L; j+=1) {
            let box_name = "#target_box_"+i+j;
            $(box_name).css("background-image", 'url(assets/empty.png)');
        }
    }
    render_shape_list(target, "#target_box_");
}

// experiment for successive success
function succ_S0_L0(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        var new_utrs = S0(target_id, utters);
        const random_utr = new_utrs[Math.floor(Math.random() * new_utrs.length)];
        utters.push(random_utr);
        
        let l0_candidates = Array.from(L0(said_to_dict(utters)));
        results.push([target_id, 'algorithm', 'S0', 'white', utters.length, 1.0 / l0_candidates.length])
        if (l0_candidates.length == 1) {
            return;
        }
    }    
}

function succ_S1_L0(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
        
        let l0_candidates = Array.from(L0(said_to_dict(utters)));
        results.push([target_id, 'algorithm', 'S1', 'white', utters.length, 1.0 / l0_candidates.length])
        if (l0_candidates.length == 1) {
            return;
        }
    }    
}

function succ_S1_L1(target_id) {
    var utters = [];
    for (var i = 0; i < 49; i++) {
        const new_utr = next_S1_utter(target_id, utters);
        utters.push(new_utr);
        // get botht the candidate set targets and associated logprobability
        let l1_candidates = L1(said_to_dict(utters), true);

        // unzip them, and normalise the logpr
        let l1_targets = l1_candidates.map(x => x[1]);
        let l1_neglogpr = l1_candidates.map(x => x[0]);
        let normed_probs = normalise(l1_neglogpr);

        // record the data and push
        results.push([target_id, 'algorithm', 'S1', 'blue', utters.length, normed_probs[l1_targets.findIndex(x => x == target_id)] ])
        if (l1_candidates.length == 1) {
             return;
        }
    }    
}

function experiment_succ(to_run, n_trials) {
    sample_problems.forEach(x => {
        var rounds = [];
        for (var attempts = 0; attempts < n_trials; attempts++) {
            
            // control randomness here by re-freshing
            L0SETS = {};
            solved_instances = {};
            for (var shapid = 0; shapid < all_shapes.length; shapid++){
                random_shape_order[shapid] = Math.random();
            }

            let round = to_run(x);
        }
        console.log("done with ", x);
    });    
}

function replay_human_data(target_id, user_id, robot_id, rec_examples) {
    var all_utters = [];
    Object.entries(rec_examples).forEach(([key, value]) => {
        all_utters.push([[Number(key[0]), Number(key[2])], value]);
    });

    var utters = [];
    var ret = [];

    if (robot_id == 0) {

        for (var i = 0; i < all_utters.length; i++) {
            const new_utr = all_utters[i];
            utters.push(new_utr);
            // get both the candidate set targets and associated logprobability
            let l0_candidates = Array.from(L0(said_to_dict(utters)));
            results.push([target_id, 'human', user_id, 'white', utters.length, 1.0 / l0_candidates.length])
        }       
    }

    if (robot_id == 1) {
        for (var i = 0; i < all_utters.length; i++) {
            const new_utr = all_utters[i];
            utters.push(new_utr);
            // get botht the candidate set targets and associated logprobability
            let l1_candidates = L1(said_to_dict(utters), true, true);

            // unzip them, and normalise the logpr
            let l1_targets = l1_candidates.map(x => x[1]);
            let l1_neglogpr = l1_candidates.map(x => x[0]);
            let normed_probs = normalise(l1_neglogpr);

            // // record the data and push
            // console.log("find it ?");
            let target_index = l1_targets.findIndex(x => x == target_id);
            if (target_index == -1) {
                return;
            }

            let norm_prob = normed_probs[target_index];
            // console.log(l1_candidates.length, norm_prob);
            results.push([target_id, 'human', user_id, 'blue', utters.length, norm_prob]);
        }       
    }

}

function replay_human_data_consistent_over_time(target_id, user_id, robot_id, rec_examples) {
    var all_utters = [];
    Object.entries(rec_examples).forEach(([key, value]) => {
        all_utters.push([[Number(key[0]), Number(key[2])], value]);
    });

    // only go up to 10
    if (all_utters.length > 10) {
        return;
    }

    var utters = [];
    var ret = [];

    for (var i = 0; i < all_utters.length; i++) {
        const new_utr = all_utters[i];
        utters.push(new_utr);
        // get both the candidate set targets and associated logprobability
        let l0_candidates = Array.from(L0(said_to_dict(utters)));
        results.push([utters.length, robot_id, l0_candidates.length])
    }       
}

function process_human_data() {
    var ctrr = 0;
    for (let [user_id, value] of Object.entries(human_data)) {
        ctrr += 1;
        console.log("on user id ", user_id, " number ", ctrr, " of ", Object.keys(human_data).length);
        console.log("time is ", new Date().getMinutes());
        if ("data" in value) {
            for (let [field, problem_value] of Object.entries(value["data"])) {
                if ("examples" in problem_value) {
                    // console.log(problem_value["examples"]);
                    let trace = problem_value["all_examples"].map(x=> x.split(" "));
                    var reconstructed_examples = {};
                    for (var i = 0; i < trace.length; i++) {
                        let tr = trace[i];
                        if (tr[1] != "delete") {
                            let xxyy = tr[1].split(",");
                            reconstructed_examples[tr[0]] = [Number(xxyy[0]), Number(xxyy[1])];
                        } else {
                            delete reconstructed_examples[tr[0]];
                        }
                    }
                    if (problem_value["all_examples"].length < 20){
                        // replay_human_data(problem_value["target_id"], user_id, problem_value["robot_id"], reconstructed_examples);
                        replay_human_data_consistent_over_time(problem_value["target_id"], user_id, problem_value["robot_id"], reconstructed_examples);
                    }
                }
            }
        }
    }
}

function succ_man_L0(speaker_utters) {

}

function download_exp_data(obj){
    var data = "text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(obj));
    $('<a href="data:' + data + '" download="data.json">download JSON</a>').appendTo('#control');
}

import pickle


reference_code_file = "data/autorepair/test_bug_code.pkl"
prediction_file = "autorepair_predictions/predict_autorepair_srcml.pkl"
exec(open('configurator.py').read()) # overrides from command line or config file

references = pickle.load(open(reference_code_file, "rb"))
input_file = prediction_file
bug_type_count_dict = {"parentheses_left":1, "parentheses_right": 1, "curly_left":1, "curly_right":1, "braket_left":1, "braket_right":1, "semicolon":1}
fixed_bug_type_count_dict = {"parentheses_left":0, "parentheses_right": 0, "curly_left":0, "curly_right":0, "braket_left":0, "braket_right":0, "semicolon":0}
preds = pickle.load(open(input_file, "rb"))
removed_char_map  = {"(":"parentheses_left", ")":"parentheses_right", "{":"curly_left", "}":"curly_right", "[":"braket_left", "]":"braket_right", ";":"semicolon"}
removed_char_name_map  = {"parentheses_left":"(", "parentheses_right":")", "curly_left":"{", "curly_right":"}", "braket_left":"[", "braket_right":"]", "semicolon":";"}

all_fids = list(preds.keys()) 
number_of_functions = len(all_fids)

count_bug_fix = 0
for fid in all_fids:
    patch = references[fid]['patch']
    #patch = patch.strip()
    start_pos = references[fid]['start_pos']
    end_pos = references[fid]['end_pos']
    bug_pos = references[fid]['bug_pos']
    pred_patch = preds[fid]
    #pred_patch = pred_patch.strip()
    pred_patch = list(pred_patch)
    patch = list(patch)
    if(start_pos == 0):
        patch_bug_pos = bug_pos
    else:
        count = 0
        for i in range(start_pos, end_pos):
            if(i!= bug_pos):
                count += 1
            else:
                patch_bug_pos = count
                break
    try:

        char_name = removed_char_map[patch[patch_bug_pos]]
        bug_type_count_dict[char_name] += 1
        if(pred_patch[patch_bug_pos+1] == patch[patch_bug_pos]):
            fixed_bug_type_count_dict[char_name] += 1
            count_bug_fix += 1

    except:
        #print(fid)
        continue
for char_type in list(fixed_bug_type_count_dict.keys()):
    accuracy = fixed_bug_type_count_dict[char_type] / bug_type_count_dict[char_type]
    char_type = removed_char_name_map[char_type]
    print(f"accuracy for {char_type}: {round(accuracy, 2)}")
#print(count_bug_fix)
print(f"bug_fix_rate: {count_bug_fix/number_of_functions}")

def calc_running_avg(prev_avg, prev_times, new_avg):
    tot_times = prev_times + 1
    prev_mult = prev_times / tot_times
    return (prev_avg * prev_mult) + (new_avg / tot_times)

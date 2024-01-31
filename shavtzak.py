DAY_HOURS = [6, 8, 10, 12, 14, 16, 18, 20]
WEEK_DAYS = ['ב','ג','ד','ה','ו','ש','א']
NIGHT_HOURS = [22, 0, 2, 4]
SHIFT_HOURS = sorted(NIGHT_HOURS + DAY_HOURS)

DAY_SLOTS = 2
NIGHT_SLOTS = 4

SHIFT_SLOTS = {h: DAY_SLOTS if h in DAY_HOURS else NIGHT_SLOTS
               for h in SHIFT_HOURS}

NAME_ORDER = list(name.decode().strip() for name in open('order.txt', 'rb').readlines())
REUVEN = 'ראובן'
NAME_ORDER

NEW_VACATION = True

def make_shift(names, vacations, vac_end, weekday):
        shifts = []
        vac_start = {}
        for i,h in enumerate(SHIFT_HOURS):
                vac_start[h] = []
                slots = DAY_SLOTS if h in DAY_HOURS else NIGHT_SLOTS
                shift_names = []
                remove_from_names = []
                
                while len(shift_names) < slots:
                        
                        if h == 4 and REUVEN in names:
                                names.remove(REUVEN)
                                name = REUVEN
                        elif vac_end[h]:
                                name = vac_end[h].pop(0)
                        else:                        
                                name = names.pop(0)

                        if name in vacations:
                                if NEW_VACATION:
                                        vac_start[h].append(name)
                                        continue
                                else:
                                        assert 0, "unsupported"
                                        if weekday == 6: #shabat
                                                vac_start.setdefault(4, []).append(name)
                                        else:
                                                vac_start.setdefault(8, []).append(name)
                                        if h >= 6:
                                                continue
                                        else:
                                                remove_from_names.append(name)

                        shift_names.append(name)

                shifts.append((h,list(shift_names)))
                while remove_from_names:
                        shift_names.remove(remove_from_names.pop(0))
                        
                names += shift_names

                # move to next hour if couldnt put in all that returned from vacation
                if vac_end[h]:
                        leftover = vac_end[h]
                        try:
                                next_h = SHIFT_HOURS[i+1]
                                vac_end[next_h] = leftover + vac_end[next_h]
                        except:
                                # if this is the last hour of the day
                                # add him to next day first shift 00:00
                                vac_start[0] = leftover + vac_start[0]
                        
        return shifts, vac_start

import copy
from datetime import datetime
def make_days_shift(days, vacations):
        name_order = list(NAME_ORDER)
        vac_start = {h: [] for h in SHIFT_HOURS}
        all_shifts = []
        for day in days:
                date = f'{day[0]}.{day[1]}.2024'
                dt = datetime.strptime(date, '%d.%m.%Y')
                
                vac_end = copy.deepcopy(vac_start)
                shifts, vac_start = make_shift(name_order, vacations[day], vac_end, dt.weekday())
                all_shifts.append((day, shifts,vac_start))
        return all_shifts


from datetime import datetime

def shift_to_csv(all_shifts, fname):
        lines = [',,,,ש"ג,ש"ג,פטרול,פטרול']
        for day, shifts, _ in all_shifts:
                for i, shift in enumerate(shifts):
                        date = f'{day[0]}.{day[1]}.2024'
                        meta = ''
                        if i == 0:
                                dt = datetime.strptime(date, '%d.%m.%Y')
                                meta = f'{WEEK_DAYS[dt.weekday()]}'
                        if i == 1:
                                meta = date
                        start, slots = shift
                        end = 0 if start == 22 else start + 2
                        line = f'{meta},{start:02}:00,-,{end:02}:00,' + ','.join(slots)
                        lines.append(line)
                        
        
        with open(fname, 'w', encoding='utf-8-sig') as f:
                f.write('\n'.join(lines))
                

from collections import OrderedDict
vacations = OrderedDict({
        (25,1): ['רינגר', 'מלאכי'],
        (26,1): ['מלאכי'],
        (27,1): ['מלאכי', 'ידידיה'],
        (28,1): [],
        (29,1): ['ידידיה', 'אבנר'],
        (30,1): [],
        (31,1): []
})
days = vacations.keys()

all_shifts = make_days_shift(days, vacations)

FNAME = 'list-reuven.csv'
shift_to_csv(all_shifts, FNAME)

import pandas as pd
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.read_csv(FNAME).fillna('')
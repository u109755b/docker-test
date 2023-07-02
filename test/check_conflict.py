from collections import Counter


class record_management:
    def __init__(self):
        self.locked_records = []
        self.peer_records = {}
        
    def diff(self, list1, list2):
        counter1 = Counter(list1)
        counter2 = Counter(list2)
        diff_counter = counter1 - counter2
        return list(diff_counter.elements())
    
    def check_line(self, peer_name, action):
        if action[0] == '[':
            self.peer_records[peer_name] = list(eval(action))
            
        elif 'fail' in action:
            records = self.peer_records[peer_name]
            self.peer_records[peer_name] = []
            if 'locl' in action:
                return f"local lock failed {sorted(records)}"
            return f"global lock failed {sorted(records)}"
        
        elif action == 'succeeded':
            records = self.peer_records[peer_name]
            self.locked_records.extend(records)
            return f"succeeded {sorted(records)}"
            
        elif action == 'released':
            records = self.peer_records[peer_name]
            self.locked_records = self.diff(self.locked_records, records)
            return f"released {sorted(records)}"
        
        elif action == 'abort':
            records = self.peer_records[peer_name]
            self.locked_records = self.diff(self.locked_records, records)
            return f"abort {sorted(records)}"
        
        else:
            return False
        return False


alliance = record_management()
provider = record_management()
with open('data1.txt', 'r') as file:
    for line in file:
        line = line.strip().split('|')      # alliance1-proxy    | [10, 37, 46, 23]
        peer_name = line[0].split('-')[0]   # alliance1
        action = line[1].strip()            # [10, 37, 46, 23]
        # peer_names.append(peer_name)
        # actions.append(action)
        
        peer_num = int(peer_name[8:])
        if peer_name[:8] == 'alliance':
            ret = alliance.check_line(peer_name, action)
        else:
            ret = provider.check_line(peer_name, action)
        if ret:
            if "succeeded" in ret or "released" in ret or "abort" in ret:
                print("")
                records = alliance.locked_records
                print(f"alliance locked records: {sorted(list(records))} {len(records)}")
                records = provider.locked_records
                print(f"provider locked records: {sorted(list(records))} {len(records)}")
            print(f"{peer_name}: {ret}")
        
        
# print("fail" in "afjwidonfailfaekiodngo")
# print(peer_names[:10])
# print(actions[:10])


import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy


class Rules:
    def __init__(self, data):
        self.data = data

    def rules(self, status):
        rules_check = []
        actions = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            for rule in self.data:
                print(rule['rule_name'])
                rules_check.append(executor.submit(check_rule, rule=rule, status=status))

            for action in as_completed(rules_check):
                actions.append(
                    {
                        'rule_name': rule['rule_name'],
                        'result': action.result(),
                        'rule_timer': rule['rule_timer'],
                        'rule_function': rule['rule_function']
                    }
                )

            return actions

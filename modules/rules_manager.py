import datetime
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.hue_manager import HueAPI
import numpy
import pandas


def op_condition(condition, status):
    op_type = condition['condition_type'].split('op_')

    op = {'average': numpy.mean(status[condition['condition_check']]),
          'sum': numpy.sum(status[condition['condition_check']]),
          'min': numpy.min(status[condition['condition_check']]),
          'max': numpy.max(status[condition['condition_check']]),
          'median': numpy.median(status[condition['condition_check']])
          }

    value = op[op_type[1]]

    if \
            eval(
                '{status}{logic}{condition}'.format(
                    status=value,
                    logic=condition['condition_logic'],
                    condition=condition['condition_value']
                )
            ):
        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_check'], " Pass", value, condition['condition_logic'],
            condition['condition_value']))

        return True
    else:
        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_check'], " Fail", value, condition['condition_logic'],
            condition['condition_value']))

        return False


def hue_condition(condition, status):
    hue_check = condition['condition_check'].split('.')
    if \
            eval(
                '{status}{logic}{condition}'.format(
                    status=status[hue_check[0]][hue_check[1]],
                    logic=condition['condition_logic'],
                    condition=condition['condition_value']
                )):

        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_type'], " Pass", status[hue_check[0]][hue_check[1]], condition['condition_logic'],
            condition['condition_value']))

        return True
    else:
        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_type'], " Fail", status[hue_check[0]][hue_check[1]], condition['condition_logic'],
            condition['condition_value']))

        return False


def time_condition(condition):
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")

    if \
            condition['condition_logic'] == '>=' and \
            current_time >= condition['condition_value']:
        result = True

    elif \
            condition['condition_logic'] == '<=' and \
            current_time <= condition['condition_value']:
        result = True

    elif \
            condition['condition_logic'] == '==' and \
            current_time == condition['condition_value']:
        result = True

    elif \
            condition['condition_logic'] == '<' and \
            current_time < condition['condition_value']:
        result = True

    elif \
            condition['condition_logic'] == '>' and \
            current_time > condition['condition_value']:
        result = True
    else:
        result = False

    if result:
        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_type'], " Pass", current_time, condition['condition_logic'],
            condition['condition_value']))
    else:
        print('{:10}*{:6}* | {:2} {:2} {:2} |'.format(
            condition['condition_type'], " Fail", current_time, condition['condition_logic'],
            condition['condition_value']))

    return result


def check_condition(condition, status):

    if 'op_' in condition['condition_type']:
        return op_condition(condition, status)

    elif 'hue' in condition['condition_type']:
        return hue_condition(condition, status)

    elif 'time' in condition['condition_type']:
        return time_condition(condition)


def check_rule(rule, status):
    conditions_check = []
    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for condition in rule['conditions']:
            conditions_check.append(
                executor.submit(check_condition, condition=condition, status=status)
            )

        for result in as_completed(conditions_check):
            results.append(result.result())

        if [True] * len(results) == results:
            return rule['rule_command']


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

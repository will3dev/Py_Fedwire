import random
import datetime
import tag_ids

from datetime import datetime as dt

# CTR transactions: 1500, 1510, 1520, 2000,
# 3100, 3320, 3400, 3600, 42000, 5000, 6000

FORMAT_VERSION = '30'
ENVIRONMENT_TEST = 'T'
ENVIRONMENT_PRODUCTION = 'P'
MESSAGE_DUPLICATION_ORIGINAL = ''
MESSAGE_DUPLICATION_RESEND = 'P'

class Batch:
    # this will contain all entry objects and populates larger file
    def __init__(self, total_dollars, transaction_count, transactions):
        self.total_dollars = total_dollars
        self.transaction_count = transaction_count
        self.transactions = transactions

    @classmethod
    def add_all_transactions(cls, transactions):
        total_dollars = 0
        transaction_count = 0

        for t in transactions:
            trans_dict = t.entry_dict
            amnt = float(
                add_decimal(trans_dict[tag_ids.AMOUNT])
            )
            total_dollars += amnt
            transaction_count += 1

        return cls(total_dollars, transaction_count, transactions)

    def add_single_transaction(self, transaction):
        trans_dict = transaction.entry_dict
        amnt = float(
            add_decimal(trans_dict[tag_ids.AMOUNT])
        )

        self.total_dollars += amnt
        self.transaction_count += 1
        self.transactions.append(transaction)


    def create_batch(self):
        # processes and adds all lines to one file
        # returns string with a lines of entries
        batch = ''
        for transaction in self.transactions:
            t = transaction.create_entry() + '\n'
            batch += t

        return batch


class Transaction:
    # holds the tags and produces the formatted entry
    def __init__(self, all_tags):
        # list of all tags made up in entry
        self.all_tags = all_tags

    def create_entry(self):
        # processes and joins tag to create entry
        self.all_tags.sort(key=lambda t: int(t.tag_code))
        entry = ''
        for tag in self.all_tags:
            entry += tag.full_tag

        return entry

    @property
    def entry_dict(self):
        e = {}
        for tag in self.all_tags:
            e[tag.tag_code] = tag.tag_element

        return e


class Tag:
    def __init__(self, tag_code, tag_element):
        self.tag_code = tag_code
        self.tag_element = tag_element

    @property
    def full_tag(self):
        return '{' + self.tag_code + '}' + self.tag_element

    @classmethod
    def sender_supplied_info(cls, is_production: bool, is_duplication=False):
        test_production_code = ENVIRONMENT_PRODUCTION if is_production else ENVIRONMENT_TEST
        message_duplication_code = MESSAGE_DUPLICATION_RESEND if is_duplication else MESSAGE_DUPLICATION_ORIGINAL
        user_request_correlation = fill_space('', 8)

        tag_element = FORMAT_VERSION + user_request_correlation + test_production_code + message_duplication_code

        return cls(tag_ids.SENDER_SUPPLIED_INFORMATION, tag_element)

    @classmethod
    def type_subtype(cls, type, subtype):
        tag_element = type + subtype
        return cls(tag_ids.TYPE_SUBTYPE, tag_element)

    @classmethod
    def imad(cls, input_cycle_date: datetime.datetime, input_sequence_number, input_source=random.randrange(0, 100000000)):
        input_cycle_date = input_cycle_date.strftime('%Y%m%d')
        input_source = fill_zeros(input_source, 8)
        input_sequence_number = fill_zeros(input_sequence_number, 6)

        tag_element = input_cycle_date + input_source + input_sequence_number

        return cls(tag_ids.IMAD, tag_element)

    @classmethod
    def amount(cls, amnt):
        return cls(tag_ids.AMOUNT, fill_zeros(amnt, 12))

    @classmethod
    def sender_DI(cls, routing_number, receiver_short_name):
        routing_number = str(routing_number)
        receiver_short_name = add_delimiter(receiver_short_name, 18)

        tag_element = routing_number + receiver_short_name

        return cls(tag_ids.SENDER_DI, tag_element)

    @classmethod
    def receiver_DI(cls, routing_number, receiver_short_name):
        routing_number = str(routing_number)
        receiver_short_name = add_delimiter(receiver_short_name, 18)

        tag_element = routing_number + receiver_short_name

        return cls(tag_ids.RECEIVER_DI, tag_element)

    @classmethod
    def business_function_code(cls, code):
        return cls(tag_ids.BUSINESS_FUNCTION_CODE, code)

    @classmethod
    def sender_reference(cls, reference_number=0):
        if reference_number == 0:
            reference_number = generate_sender_reference_number()

        reference_number = add_delimiter(str(reference_number), 16)

        return cls(tag_ids.SENDER_REFERENCE, reference_number)

    @classmethod
    def beneficiary(cls, id_code, identifier, name, address: list):
        identifier = add_delimiter(identifier, 34)
        name = add_delimiter(name, 35)
        address = ''.join([add_delimiter(a, 35) for a in address])

        tag_element = id_code + identifier + name + address

        return cls(tag_ids.BENEFICIARY, tag_element)

    @classmethod
    def originator(cls, id_code, identifier, name, address: list):
        identifier = add_delimiter(identifier, 34)
        name = add_delimiter(name, 35)
        address = ''.join([add_delimiter(a, 35) for a in address])

        tag_element = id_code + identifier + name + address

        return cls(tag_ids.ORIGINATOR, tag_element)

    @classmethod
    def originator_to_beneficiary_info(cls, message: list):
        message = [
            add_delimiter(m, 35)
            for m in message
        ]
        tag_element = ''.join(message)

        return cls(tag_ids.ORIGINATOR_TO_BENEFICIARY, tag_element)


def add_delimiter(value, field_length=0):
    # this will be used to add the delimiter icon
    # needs to identify tags that don't meet the max length
    value = str(value)
    value_length = len(value)

    if value_length < field_length:
        return value + tag_ids.VARIABLE_LENGTH_DELIMITER

    elif value_length > field_length:
        cut = value_length - field_length
        return value[:-cut] + tag_ids.VARIABLE_LENGTH_DELIMITER

    else:
        return value + tag_ids.VARIABLE_LENGTH_DELIMITER


def fill_space(current_value, field_length):
    space_to_fill = field_length - len(str(current_value))
    return current_value + (space_to_fill * ' ')


def fill_zeros(current_value, field_length):
    current_value = str(current_value)
    space_to_fill = field_length - len(current_value)
    return (space_to_fill * '0') + current_value


def generate_sender_reference_number():
    return str(random.randrange(1, 10000000000000000))

def add_decimal(value):
    value_list = [v for v in value]
    value_list.insert(-2, '.') # insert the decimal point
    return ''.join(value_list)

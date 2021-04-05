import datetime as dt
import fedwire_codes as fw
from format import Batch, Transaction, Tag


transaction_listing = [
    Transaction([
        Tag.sender_supplied_info(is_production=False),
        Tag.sender_reference(),
        Tag.type_subtype(fw.FUNDS_TRANSFER, fw.BASIC_FUNDS_TRANSFER),
        Tag.imad(dt.datetime.now(), 1),
        Tag.amount(12500), # should be number without decimal last two characters are cents
        Tag.sender_DI('011000138', 'Bank of America'),
        Tag.receiver_DI('021000021', 'Chase Bank'),
        Tag.business_function_code(fw.CUSTOMER_TRANSFER),
        Tag.beneficiary(
            fw.DEMAND_DEPOSIT_ACCOUNT_NUM,
            '420356588',
            'John Test',
            ['5 main street', 'New York City', 'NY 10001']
        ),
        Tag.originator(
            fw.DEMAND_DEPOSIT_ACCOUNT_NUM,
            '123384247',
            'James Francis',
            ['2 South St', 'Boston', 'MA 02101']
        ),
        Tag.originator_to_beneficiary_info(['Sample Ref', '01347723'])
    ]),
    Transaction([
        Tag.sender_supplied_info(is_production=False),
        Tag.sender_reference(),
        Tag.type_subtype(fw.FUNDS_TRANSFER, fw.BASIC_FUNDS_TRANSFER),
        Tag.imad(dt.datetime.now(), 1),
        Tag.amount(52500), # should be number without decimal last two characters are cents
        Tag.sender_DI('011000138', 'Bank of America'),
        Tag.receiver_DI('021000021', 'Chase Bank'),
        Tag.business_function_code(fw.CUSTOMER_TRANSFER),
        Tag.beneficiary(
            fw.DEMAND_DEPOSIT_ACCOUNT_NUM,
            '23429387',
            'James Test',
            ['5 North Ave', 'New York City', 'NY 10009']
        ),
        Tag.originator(
            fw.DEMAND_DEPOSIT_ACCOUNT_NUM,
            '234980880',
            'Martha Test',
            ['5 Yawkey Way', 'Boston', 'MA 02101']
        ),
        Tag.originator_to_beneficiary_info(['TEST WIRE'])
    ])
]

batch = Batch.add_all_transactions(transaction_listing)

print(batch.create_batch())
print('BATCH TOTALS:')
print('Total Dollars - $', batch.total_dollars)
print('Transaction Count - ', batch.transaction_count)

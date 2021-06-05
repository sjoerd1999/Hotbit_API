#!../env/bin/python

from decimal import Decimal, getcontext

from utils import tprint

def get_decimal_places_for(d):
    return len( str(d).split('.')[1].rstrip('0') )

import traceback

first_warning = True
class ナ:
    def __init__(ᬑ, x, decimal_places=8, from_float=False):
        ᬑ.decimal_places = decimal_places
        getcontext().prec=20

        if x is None or x == 'None':
            x = 0

        if isinstance(x, float) and not from_float:
            global first_warning
            if first_warning:
                tprint('⛔️ One-time warning: Initializing from float')

                for line in traceback.format_stack():
                    print(line.strip())

                first_warning = False

        # internally store full precision
        ᬑ.value = x.value if isinstance(x, ナ) else \
            Decimal(x)
            # Decimal(x).quantize(
            #     Decimal('1.' + '0'*decimal_places),
            #     rounding=rounding_upon_init
            #     )


    def quantize_down_with_template(ᬑ, template):
        template_as_decimal = template.value if isinstance(template, ナ) else Decimal(template)
        w = template_as_decimal.normalize()  # 0.00100 -> 0.001
        ᬑ.value = ᬑ.value.quantize(w, 'ROUND_DOWN')


    def is_integral(ᬑ):
        return ᬑ.value % 1 == 0


    # 0.01 can be represented as 1 with 2 shifts
    def pack(ᬑ):
        tmp = Decimal(ᬑ.value)
        shifts = 0
        while Decimal(str(tmp).split('.')[0]) != tmp:
            tmp *= 10
            shifts += 1
        return int(tmp), shifts

    def unpack(as_int, shifts):
        return ナ(as_int) / 10**shifts

    # pack into bytes, returning a string like '01101101010`
    # NOTE: this string will be of variable length
    def bpack(ᬑ):
        as_int, shifts = ᬑ.pack()
        signbit = 1 if as_int < 0 else 0

        bin4 = lambda d: bin(d).split('0b')[1]

        bPayload = bin4(as_int)

        padded_binary4 = lambda i, N: bin4(i).zfill(N)

        return ''.join([
                str(signbit),
                padded_binary4(shifts, 4),
                padded_binary4(len(bPayload), 6),
                bPayload
            ])

    # Unpacker looks in binary array at location 'offset',
    # pulls out the item, returning new offset
    def bunpack(b, offset=0):
        sign = -1 if b[offset+0] == '1' else 1
        shifts  = int(b[offset+1  : offset+5         ], 2)
        nDigits = int(b[offset+5  : offset+11        ], 2)
        as_int  = int(b[offset+11 : offset+11+nDigits], 2)

        return sign * ナ.unpack(as_int, shifts), offset+11+nDigits

    # TODO
    # def mathfunc(rhs, func):
    #     _lhs = 

    # ナ * rhs
    def __mul__(ᬑ, rhs):
        # rhs_as_decimal = rhs.value if isinstance(rhs,ナ) else Decimal(rhs)
        getcontext().rounding = 'ROUND_DOWN'
        # x = ᬑ.value * rhs_as_decimal
        return ナ(ᬑ.value * ナ(rhs).value, ᬑ.decimal_places)

    # lhs * ナ
    def __rmul__(ᬑ, lhs):
        return ᬑ.__mul__(lhs)


    def __truediv__(ᬑ, rhs):
        # rhs_as_decimal = rhs.value if isinstance(rhs,ナ) else Decimal(rhs)
        getcontext().rounding = 'ROUND_DOWN'
        # x = ᬑ.value / rhs_as_decimal
        return ナ(ᬑ.value / ナ(rhs).value, ᬑ.decimal_places)

    def __rtruediv__(ᬑ, lhs):  # lhs / ᬑ
        # lhs_as_decimal = lhs.value if isinstance(lhs,ナ) else Decimal(lhs)
        getcontext().rounding = 'ROUND_DOWN'
        # x = lhs_as_decimal / ᬑ.value
        return ナ(ナ(lhs).value / ᬑ.value, ᬑ.decimal_places)


    def __add__(ᬑ, rhs):
        # rhs_as_decimal = rhs.value if isinstance(rhs,ナ) else Decimal(rhs)
        getcontext().rounding = 'ROUND_DOWN'
        # x = ᬑ.value + rhs_as_decimal
        return ナ(ᬑ.value + ナ(rhs).value, ᬑ.decimal_places)
        
    def __radd__(ᬑ, lhs):
        return ᬑ.__add__(lhs)

    # ᬑ - rhs, we round UP rhs, so that result is <= real result
    def __sub__(ᬑ, rhs):
        rhsナ = ナ(rhs) # rhs.value if isinstance(rhs,ナ) else Decimal(rhs, rounding_upon_init='ROUND_UP')
        # x = ᬑ.value - rhsナ.value
        getcontext().rounding = 'ROUND_DOWN'
        return ナ(ᬑ.value - ナ(rhs).value, ᬑ.decimal_places)


    def __repr__(ᬑ):
        getcontext().rounding = 'ROUND_DOWN'
        rounded_down = round(ᬑ.value, ᬑ.decimal_places)

        # Alternative:
        # q = Decimal(10) ** -ᬑ.decimal_places  # 2 places --> '0.01'
        # rounded_down = ᬑ.value.quantize(q, 'ROUND_DOWN')

        no_sci_notation = format(rounded_down, 'f')
        return str(no_sci_notation)

    def compare(ᬑ, rhs, comparison_func):
        _lhs = Decimal(str(ᬑ))
        _rhs = Decimal(str(ナ(rhs, ᬑ.decimal_places)))

        return comparison_func(_lhs, _rhs)

    def __eq__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l==r)

    def __ne__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l!=r)

    def __lt__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l<=r)

    def __gt__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l>r)

    def __le__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l<=r)

    def __ge__(ᬑ, rhs):
        return ᬑ.compare(rhs, lambda l,r: l>=r)

    def as_float(ᬑ):
        return float(ᬑ.value)

if __name__ == '__main__':
    assert(get_decimal_places_for(ナ('0.00100000')) == 3)

    def eq(a, b, text):
        print('✅' if str(a) == str(b) else '❌', a, b, text)

    # padding
    print(ナ('1.23',4))
    eq(ナ('1.23',4), '1.2300', 'padding')

    # truncation
    eq(ナ('1.234',2), '1.23', 'truncation')
    eq(ナ('1.238',2), '1.23', 'rounding down')

    # internal storage is full precision, output is truncated
    eq(ナ('0.05',1), '0.0', 'internal high precision')
    eq(2 * ナ('0.05',1), '0.1', 'internal high precision')

    eq(ナ('1.238').quantize_down_with_template('0.01000000'), '1.23000000', 'quantize_down_with_template')

    # multiply commutes
    eq(ナ('0.05',1) * 2,  2 * ナ('0.05',1), '* commutes')

    # converts scientific notation to decimal
    eq(ナ('1.23E-1',4), '0.1230', 'converts scientific notation to decimal')

    # DOESN'T convert decimal to scientific notation
    eq(ナ('.00000095623',8), '0.00000095', 'convert decimal to scientific notation')
    eq(ナ('9.5623E-7',8), '0.00000095', 'convert decimal to scientific notation')

    eq(ナ('0.99',2) + ナ('0.01',2), '1.00', '+ operator')

    eq(ナ(30) / 50000, '0.00060000', 'Division')

    eq(ナ('1.23',4) - ナ('1.23001',4), '-0.0000', 'subtraction')
    eq(ナ('1.23',4) - ナ('1.23009',4), '-0.0000', 'subtraction')

    eq(ナ('1.23',4) - ナ('0.23001',4), '0.9999', 'subtraction')
    eq(ナ('1.23',4) - ナ('0.23009',4), '0.9999', 'subtraction')

    eq(ナ('1.234',2) == ナ('1.236',2), True, '==')
    eq(ナ('1.24',2) >= ナ('1.23',2), True, '>=')

    print('Expect warning:')
    print(ナ(0.99))

    print('✅ All unit tests passed')

    def pack_test(x):
        ナx = ナ(x)
        as_int, shifts = ナx.pack()
        unpacked = ナ.unpack(as_int, shifts)
        print(f'Pack {ナx} -> ({as_int}, {shifts}) -> Unpack -> {unpacked}')

    pack_test('0.00123')
    pack_test('42')
    pack_test('42.00000001')

    def bpack_test(L):
        b = ''.join( [ナ(x).bpack() for x in L] )

        M = [None]*len(L)
        offset=0
        for i in range(len(L)):
            M[i], offset = ナ.bunpack(b, offset)

        for l,m in zip(L,M):
            print(l,m)

    bpack_test([
        ナ('0'),
        ナ('-1.00023001'),
        ナ('9999999.00000001'),
        ])

    print(ナ(3) / "5")

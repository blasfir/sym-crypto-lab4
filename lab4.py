from itertools import product
from scipy.stats import norm

n1 = 25
n2 = 26
N1 = 222
N2 = 119
C1 = 71
C2 = 74


def extend_lfsr(state, taps, length):
    while len(state) < length:
        new_bit = 0
        for t in taps:
            new_bit ^= state[-t]
        state.append(new_bit)
    return state


def gifford_generator(x_bits, y_bits, s_bits):
    result = []
    for x, y, s in zip(x_bits, y_bits, s_bits):
        bit = (s & x) ^ ((1 ^ s) & y)
        result.append(bit)
    return result


def search_lfsr_candidates(N, C, z_i, taps, reg_len):
    initial = [0] * (reg_len - 1) + [1]
    state = initial[:]
    sequence = extend_lfsr(state[:], taps, N)
    candidates = []
    while True:
        R = 0
        for bit, z_bit in zip(sequence, z_i):
            if bit == z_bit:
                R += 1
        if R > C:
            candidates.append((state[:], R))
        new_bit = 0
        for t in taps:
            new_bit ^= state[-t]
        state = state[1:] + [new_bit]
        sequence = sequence[1:] + [new_bit]
        if state == initial:
            break
    return candidates


def are_l1_l2_compatible(x_i, y_i, z_i):
    for i in range(len(z_i)):
        x = x_i[i]
        y = y_i[i]
        z = z_i[i]
        if (z == 1 and x == 0 and y == 0) or (z == 0 and x == 1 and y == 1):
            return False
    return True


def find_compatible_pairs(l1_candidates, l2_candidates, z_i, len=200):
    compatible_pairs = []
    for l1_state, _ in l1_candidates:
        for l2_state, _ in l2_candidates:
            x_i = extend_lfsr(l1_state[:], [25, 22], len)
            y_i = extend_lfsr(l2_state[:], [26, 25, 24, 20], len)
            z_cut = z_i[:len]
            if are_l1_l2_compatible(x_i, y_i, z_cut):
                compatible_pairs.append((l1_state[:], l2_state[:]))
    return compatible_pairs


def find_compatible_pairs_2(compatible_pairs, z_i):
    compatible_pairs_2 = []
    for l1_state, l2_state in compatible_pairs:
        x_i = extend_lfsr(l1_state[:], [25, 22], len(z_i))
        y_i = extend_lfsr(l2_state[:], [26, 25, 24, 20], len(z_i))
        if are_l1_l2_compatible(x_i, y_i, z_i):
            compatible_pairs_2.append((l1_state[:], l2_state[:]))
    return compatible_pairs_2


def build_theoretical_s(x_i, y_i, z_i):
    s_template = []
    for x, y, z in zip(x_i, y_i, z_i):
        if z == x and z != y:
            s_template.append(1)
        elif z == y and z != x:
            s_template.append(0)
        elif z != x and z != y:
            return None
        elif z == x == y:
            s_template.append('_')
    return s_template


def generate_all_s_variants(template):
    unknown_indices = [i for i, val in enumerate(template) if val == '_']
    all_variants = []
    for bits in product([0, 1], repeat=len(unknown_indices)):
        s = template[:]
        for idx, bit in zip(unknown_indices, bits):
            s[idx] = bit
        all_variants.append(s)
    return all_variants


def find_correct_l1_l2_l3(compatible_pairs, z_i):
    for l1_state, l2_state in compatible_pairs:
        x_i = extend_lfsr(l1_state[:], [25, 22], len(z_i))
        y_i = extend_lfsr(l2_state[:], [26, 25, 24, 20], len(z_i))
        s_template = build_theoretical_s(x_i, y_i, z_i)
        if s_template is None:
            continue
        s_variants = generate_all_s_variants(s_template)
        for s in s_variants:
            z_check = gifford_generator(x_i, y_i, s)
            if z_check == z_i:
                l3 = s[:27]
                return l1_state[:], l2_state[:], l3
    return None, None, None


with open("text.txt", encoding="utf-8") as f:
    z_i = f.read()
    z_i2 = int(z_i)
    z_i = [int(bit) for bit in z_i]

"""l1_candidates = search_lfsr_candidates(N1, C1, z_i, [25, 22], n1)
l2_candidates = search_lfsr_candidates(N2, C2, z_i, [26, 25, 24, 20], n2)

compatible_pairs = find_compatible_pairs(l1_candidates, l2_candidates, z_i)

compatible_pairs_2 = find_compatible_pairs_2(compatible_pairs, z_i)

l1, l2, l3 = find_correct_l1_l2_l3(compatible_pairs_2, z_i)

if l1 is not None:
    print("L1:", ''.join(map(str, l1)))
    print("L2:", ''.join(map(str, l2)))
    print("L3:", ''.join(map(str, l3)))"""

# 0101110001110001110001001
# 01000101011001011001011001
# 010010000010010110100100001

L1_state = [0, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1,
            1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1]

L2_state = [0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 1,
            0, 0, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1]

L3_state = [0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
            0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1]


x = extend_lfsr(L1_state, [25, 22], len(z_i))
y = extend_lfsr(L2_state, [26, 25, 24, 20], len(z_i))
s = extend_lfsr(L3_state, [27, 26, 25, 22], len(z_i))

z = gifford_generator(x, y, s)

if z_i == z:
    print()
    print("Success")

print()
print("Згенерована послідовність z:")
print("".join(str(bit) for bit in z))

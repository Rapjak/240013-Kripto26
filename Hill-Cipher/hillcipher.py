import sys
import itertools
from math import gcd

MOD = 26
MAX_MATRIX_SIZE = 8
BRUTEFORCE_MAX_N = 2
PAD_CHAR = 'X'


def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return g, x, y


def mod_inverse(a, m=MOD):
    a = a % m
    g, x, _ = extended_gcd(a, m)
    if g != 1:
        return None
    return x % m


def matrix_determinant(matrix):
    n = len(matrix)
    if n == 1:
        return matrix[0][0]
    if n == 2:
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    det = 0
    for col in range(n):
        minor = [row[:col] + row[col + 1:] for row in matrix[1:]]
        det += ((-1) ** col) * matrix[0][col] * matrix_determinant(minor)
    return det


def matrix_cofactor(matrix):
    n = len(matrix)
    cof = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [row[:j] + row[j + 1:] for k, row in enumerate(matrix) if k != i]
            cof[i][j] = ((-1) ** (i + j)) * matrix_determinant(minor)
    return cof


def matrix_transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matrix_adjugate(matrix):
    return matrix_transpose(matrix_cofactor(matrix))


def matrix_mod(matrix, mod=MOD):
    return [[val % mod for val in row] for row in matrix]


def matrix_multiply(A, B, mod=MOD):
    n = len(A)
    k = len(B)
    m = len(B[0])
    result = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            total = 0
            for x in range(k):
                total += A[i][x] * B[x][j]
            result[i][j] = total % mod
    return result


def is_invertible_mod(matrix, mod=MOD):
    det = matrix_determinant(matrix) % mod
    return gcd(det, mod) == 1


def matrix_inverse_mod(matrix, mod=MOD):
    det = matrix_determinant(matrix) % mod
    det_inv = mod_inverse(det, mod)
    if det_inv is None:
        return None
    adj = matrix_mod(matrix_adjugate(matrix), mod)
    return [[(det_inv * val) % mod for val in row] for row in adj]


def clean_text(text):
    return ''.join(ch for ch in text.upper() if ch.isalpha())


def text_to_numbers(text):
    return [ord(ch) - ord('A') for ch in text]


def numbers_to_text(numbers, mod=MOD):
    return ''.join(chr((num % mod) + ord('A')) for num in numbers)


def pad_text(text, n, pad_char=PAD_CHAR):
    sisa = len(text) % n
    if sisa != 0:
        text += pad_char * (n - sisa)
    return text


def hill_transform(numbers, matrix, mod=MOD):
    n = len(matrix)
    hasil = []
    for i in range(0, len(numbers), n):
        blok = numbers[i:i + n]
        vektor = [[nilai] for nilai in blok]
        blok_hasil = matrix_multiply(matrix, vektor, mod)
        hasil.extend(baris[0] for baris in blok_hasil)
    return hasil


def process_encrypt(data):
    n = data['n']
    key = data['key']
    plaintext = data['plaintext']
    padded_plaintext = pad_text(plaintext, n)
    numbers = text_to_numbers(padded_plaintext)
    encrypted_numbers = hill_transform(numbers, key)
    ciphertext = numbers_to_text(encrypted_numbers)
    return {'padded_plaintext': padded_plaintext, 'key': key, 'ciphertext': ciphertext}


def process_decrypt(data):
    n = data['n']
    key = data['key']
    ciphertext = data['ciphertext']
    key_inverse = matrix_inverse_mod(key)
    if key_inverse is None:
        return None
    numbers = text_to_numbers(ciphertext)
    decrypted_numbers = hill_transform(numbers, key_inverse)
    plaintext = numbers_to_text(decrypted_numbers)
    return {'key': key, 'key_inverse': key_inverse, 'plaintext': plaintext}


def find_key_known_plaintext(plaintext_numbers, ciphertext_numbers, n):
    total_dibutuhkan = n * n
    P_blok = [plaintext_numbers[i:i + n] for i in range(0, total_dibutuhkan, n)]
    C_blok = [ciphertext_numbers[i:i + n] for i in range(0, total_dibutuhkan, n)]
    P_matrix = matrix_transpose(P_blok)
    C_matrix = matrix_transpose(C_blok)
    P_inverse = matrix_inverse_mod(P_matrix)
    if P_inverse is None:
        return None
    return matrix_multiply(C_matrix, P_inverse)


def find_key_bruteforce(plaintext_numbers, ciphertext_numbers, n):
    jumlah_blok = len(plaintext_numbers) // n
    blok_p = [plaintext_numbers[i * n:(i + 1) * n] for i in range(jumlah_blok)]
    blok_c = [ciphertext_numbers[i * n:(i + 1) * n] for i in range(jumlah_blok)]
    for kombinasi in itertools.product(range(MOD), repeat=n * n):
        kandidat = [list(kombinasi[i * n:(i + 1) * n]) for i in range(n)]
        det = matrix_determinant(kandidat) % MOD
        if gcd(det, MOD) != 1:
            continue
        cocok = True
        for bp, bc in zip(blok_p, blok_c):
            vektor = [[v] for v in bp]
            hasil = matrix_multiply(kandidat, vektor)
            if [baris[0] for baris in hasil] != bc:
                cocok = False
                break
        if cocok:
            return kandidat
    return None


def process_find_key(data):
    n = data['n']
    metode = data['method']
    plaintext = data['plaintext']
    ciphertext = data['ciphertext']
    p_numbers = text_to_numbers(plaintext)
    c_numbers = text_to_numbers(ciphertext)
    if metode == 'known':
        key = find_key_known_plaintext(p_numbers, c_numbers, n)
    else:
        key = find_key_bruteforce(p_numbers, c_numbers, n)
    return {'key': key}


def process_all(mode, data):
    try:
        if mode == '1':
            return process_encrypt(data)
        elif mode == '2':
            return process_decrypt(data)
        elif mode == '3':
            return process_find_key(data)
    except Exception as e:
        display_error(f"Terjadi kesalahan tak terduga saat memproses data ({e}). "
                       f"Silakan periksa kembali input Anda dan coba lagi.")
        return None


def display_error(pesan):
    print(f"\n[ERROR] {pesan}")


def display_warning(pesan):
    print(f"\n[PERINGATAN] {pesan}")


def display_info(pesan):
    print(f"[INFO] {pesan}")


def display_matrix(matrix, label="Matriks"):
    print(f"{label}:")
    for row in matrix:
        print("   [ " + "  ".join(f"{val:3d}" for val in row) + " ]")


def display_menu():
    print("\n" + "=" * 60)
    print(" PROGRAM HILL CIPHER ".center(60, "="))
    print("=" * 60)
    print(" 1. Enkripsi teks")
    print(" 2. Dekripsi teks")
    print(" 3. Cari kunci Hill Cipher")
    print(" 4. Keluar dari program")
    print("=" * 60)


def display_welcome():
    print("\nSelamat datang di Program Hill Cipher (n x n, modulo 26 / A-Z).")


def show_output(mode, result_data):
    if result_data is None:
        return
    if mode == '1':
        print("\n--- HASIL ENKRIPSI ---")
        display_info(f"Plaintext (setelah padding jika perlu): {result_data['padded_plaintext']}")
        display_matrix(result_data['key'], "Matriks Kunci yang digunakan")
        print(f"Ciphertext hasil enkripsi : {result_data['ciphertext']}")
    elif mode == '2':
        print("\n--- HASIL DEKRIPSI ---")
        display_matrix(result_data['key'], "Matriks Kunci")
        display_matrix(result_data['key_inverse'], "Matriks Invers Kunci (mod 26)")
        print(f"Plaintext hasil dekripsi : {result_data['plaintext']}")
    elif mode == '3':
        print("\n--- HASIL PENCARIAN KUNCI ---")
        if result_data['key'] is None:
            display_error(
                "Kunci Hill Cipher TIDAK ditemukan dari data plaintext/ciphertext yang diberikan. "
                "Kemungkinan penyebab: data pasangan plaintext-ciphertext tidak konsisten, "
                "atau blok plaintext yang dipakai tidak memiliki invers modulo 26. "
                "Silakan coba dengan pasangan data lain."
            )
        else:
            display_matrix(result_data['key'], "Kunci Hill Cipher yang Ditemukan")


def input_menu_choice():
    while True:
        pilihan = input("Pilih menu (1-4): ").strip()
        if pilihan in ('1', '2', '3', '4'):
            return pilihan
        display_error("Pilihan tidak dikenali! Harap masukkan angka 1, 2, 3, atau 4 sesuai menu di atas.")


def input_matrix_size(tujuan="matriks kunci"):
    while True:
        mentah = input(f"Masukkan ukuran {tujuan} (n untuk n x n, contoh: 2 atau 3): ").strip()
        if not mentah.lstrip('-').isdigit():
            display_error("Ukuran matriks harus berupa angka bulat! Silakan masukkan ulang.")
            continue
        n = int(mentah)
        if n < 1:
            display_error("Ukuran matriks minimal adalah 1! Silakan masukkan ulang.")
            continue
        if n > MAX_MATRIX_SIZE:
            display_error(
                f"Ukuran matriks terlalu besar (maksimal {MAX_MATRIX_SIZE}x{MAX_MATRIX_SIZE}) "
                f"karena akan sangat lambat dan boros memori untuk dihitung! "
                f"Silakan masukkan ukuran yang lebih kecil."
            )
            continue
        if n > 5:
            display_warning(
                f"Ukuran matriks {n}x{n} cukup besar sehingga proses perhitungan "
                f"determinan/invers bisa memakan waktu lebih lama dari biasanya."
            )
        return n


def input_key_matrix(n):
    while True:
        print(f"\nMasukkan matriks kunci berukuran {n}x{n} (baris per baris, "
              f"elemen dipisah dengan spasi).")
        matrix = []
        for i in range(n):
            while True:
                mentah = input(f"  Baris {i + 1} ({n} angka dipisah spasi): ").strip()
                bagian = mentah.split()
                if len(bagian) != n:
                    display_error(f"Jumlah angka pada baris ini harus tepat {n} buah! Silakan masukkan ulang baris ini.")
                    continue
                try:
                    baris_angka = [int(x) for x in bagian]
                except ValueError:
                    display_error("Semua elemen matriks harus berupa angka bulat! Silakan masukkan ulang baris ini.")
                    continue
                matrix.append(baris_angka)
                break
        if not is_invertible_mod(matrix):
            display_error(
                "Matriks kunci tersebut TIDAK VALID untuk Hill Cipher karena determinannya "
                "tidak memiliki invers modulo 26 (gcd(determinan, 26) harus = 1). "
                "Silakan masukkan matriks kunci yang lain."
            )
            continue
        return matrix


def input_text(label, minimal_panjang=1):
    while True:
        mentah = input(f"Masukkan {label}: ")
        if mentah.strip() == '':
            display_error(f"{label.capitalize()} tidak boleh kosong! Silakan masukkan kembali.")
            continue
        bersih = clean_text(mentah)
        if bersih == '':
            display_error(
                f"{label.capitalize()} harus mengandung minimal satu huruf (A-Z)! "
                f"Karakter selain huruf akan diabaikan. Silakan masukkan kembali."
            )
            continue
        if bersih != mentah.strip().upper().replace(' ', ''):
            display_info(f"Karakter non-huruf pada input telah diabaikan. Teks yang diproses: {bersih}")
        if len(bersih) < minimal_panjang:
            display_error(
                f"{label.capitalize()} terlalu pendek! Dibutuhkan minimal {minimal_panjang} huruf. "
                f"Silakan masukkan kembali."
            )
            continue
        return bersih


def input_ciphertext_untuk_dekripsi(n):
    while True:
        bersih = input_text("teks cipher (ciphertext) yang ingin didekripsi")
        if len(bersih) % n != 0:
            display_error(
                f"Panjang ciphertext ({len(bersih)} huruf) harus merupakan kelipatan dari "
                f"ukuran matriks kunci ({n})! Ciphertext hasil enkripsi Hill Cipher yang valid "
                f"pasti sudah berupa kelipatan {n}. Silakan periksa kembali teks cipher Anda."
            )
            continue
        return bersih


def input_key_search_method(n):
    while True:
        print("\nMetode pencarian kunci:")
        print("  1. Known-Plaintext Attack (berdasarkan pasangan plaintext-ciphertext)")
        print("  2. Brute Force (mencoba semua kemungkinan kunci)")
        pilihan = input("Pilih metode (1-2): ").strip()
        if pilihan == '1':
            return 'known'
        elif pilihan == '2':
            if n > BRUTEFORCE_MAX_N:
                total_kombinasi = MOD ** (n * n)
                display_warning(
                    f"Metode Brute Force untuk matriks {n}x{n} harus mencoba hingga "
                    f"26^{n*n} (~{total_kombinasi:.2e}) kemungkinan kunci, yang TIDAK REALISTIS "
                    f"untuk dihitung dalam waktu wajar! Brute force hanya didukung untuk ukuran "
                    f"maksimal {BRUTEFORCE_MAX_N}x{BRUTEFORCE_MAX_N}. "
                    f"Silakan pilih metode Known-Plaintext Attack, atau gunakan ukuran matriks "
                    f"yang lebih kecil."
                )
                continue
            return 'bruteforce'
        else:
            display_error("Pilihan tidak dikenali! Harap masukkan angka 1 atau 2.")


def input_known_pair(n):
    kebutuhan_minimal = n * n
    while True:
        plaintext = input_text("teks asli (plaintext) yang diketahui", minimal_panjang=kebutuhan_minimal)
        ciphertext = input_text("teks sandi (ciphertext) yang bersesuaian dengan plaintext tersebut",
                                 minimal_panjang=kebutuhan_minimal)
        if len(plaintext) != len(ciphertext):
            display_error(
                "Panjang plaintext dan ciphertext yang diketahui harus SAMA "
                "(saling berpasangan huruf per huruf)! Silakan masukkan ulang keduanya."
            )
            continue
        if len(plaintext) < kebutuhan_minimal:
            display_error(
                f"Untuk mencari kunci berukuran {n}x{n}, dibutuhkan minimal {kebutuhan_minimal} "
                f"huruf plaintext beserta pasangan ciphertext-nya! Silakan masukkan ulang dengan "
                f"teks yang lebih panjang."
            )
            continue
        return plaintext, ciphertext


def input_yes_no(pertanyaan):
    while True:
        mentah = input(f"{pertanyaan} (y/n): ").strip().lower()
        if mentah in ('y', 'yes', 'ya'):
            return True
        if mentah in ('n', 'no', 'tidak'):
            return False
        display_error("Jawaban tidak dikenali! Harap masukkan 'y' untuk ya atau 'n' untuk tidak.")


def get_all_inputs(mode):
    data = {}
    if mode == '1':
        n = input_matrix_size("matriks kunci")
        key = input_key_matrix(n)
        plaintext = input_text("teks asli (plaintext) yang ingin dienkripsi")
        data.update(n=n, key=key, plaintext=plaintext)
    elif mode == '2':
        n = input_matrix_size("matriks kunci")
        key = input_key_matrix(n)
        ciphertext = input_ciphertext_untuk_dekripsi(n)
        data.update(n=n, key=key, ciphertext=ciphertext)
    elif mode == '3':
        n = input_matrix_size("kunci yang ingin dicari")
        metode = input_key_search_method(n)
        plaintext, ciphertext = input_known_pair(n)
        data.update(n=n, method=metode, plaintext=plaintext, ciphertext=ciphertext)
    return data


def run_hill_cipher_program():
    display_welcome()
    while True:
        display_menu()
        mode = input_menu_choice()
        if mode == '4':
            print("\nTerima kasih telah menggunakan Program Hill Cipher. Sampai jumpa!")
            break
        data = get_all_inputs(mode)
        hasil = process_all(mode, data)
        show_output(mode, hasil)
        if not input_yes_no("\nApakah Anda ingin melakukan operasi lain?"):
            print("\nTerima kasih telah menggunakan Program Hill Cipher. Sampai jumpa!")
            break


if __name__ == "__main__":
    try:
        run_hill_cipher_program()
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan paksa oleh pengguna (Ctrl+C). Sampai jumpa!")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nTerjadi kesalahan fatal pada program: {e}")
        print("Program akan ditutup. Mohon laporkan masalah ini jika terus terjadi.")
        sys.exit(1)
